"""Tiers 2 and 3: validate research candidates against evidence and decide by consensus.

For every candidate (generated/knowledge/candidates/) it gathers, per claim and corner:
    transcript  the corner notes from lap-guide videos placed on that corner (explicit, or by
                enrichment above its threshold), tested with the claim's deterministic transcript
                test; each video counts once, as confirming or contradicting, with its quote
    telemetry   the corner's metrics over the driver's laps and reference laps
                (telemetry_landmarks.corner_metrics), tested with the claim's telemetry test
    variants    the same evidence at the identical corner of another layout of the venue (turn
                markers on the same spot of the shared map; for claims that depend on the
                approach, the corners before and after must match too). Only direct evidence
                from the other layout counts, never its status, so layouts cannot confirm each
                other in a loop.
Then src/knowledge/consensus.py scores it and decides: validated, rejected or pending.

Inheritance: a claim validated on a layout from its own evidence is copied to identical corners
of the venue's other layouts that have no record of it and no contradicting evidence, with
source_track and inheritance_confidence, when its confidence times the inheritance confidence
stays above the promotion threshold.

Writes generated/knowledge/{candidates,validated,rejected}/<track_id>.json (validated is the
source of truth that build_track_knowledge_pack reads) and generated/knowledge/consensus_report.json.

Usage: python -m src.pipelines.validate_knowledge_candidates   (after enrich_corner_assignments)
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.knowledge import repository as repo
from src.knowledge.claims import CLAIMS
from src.knowledge.consensus import explain, load_config, score
from src.pipelines.enrich_corner_assignments import FIELDS, clean_turns
from src.shared.iracing_tracks import load_layouts
from src.shared.paths import GENERATED
from src.shared.telemetry_landmarks import corner_metrics

REPORT = repo.ROOT / "consensus_report.json"


# --- evidence ---------------------------------------------------------------------------------

def transcript_notes():
    """{(track_id, label): [note]} from enriched notes placed on a corner."""
    out = defaultdict(list)
    for path in (GENERATED / "corner_guidance" / "enriched").glob("*.json"):
        result = json.loads(path.read_text(encoding="utf-8"))
        for n in result["notes"]:
            if n.get("status") == "assigned":
                out[(result["track_id"], n["corner_id"])].append({**n, "video_id": result["video_id"]})
    return out


def transcript_evidence(claim, notes):
    """{"confirm": [...], "contradict": [...]}: one entry per video, with the note as provenance."""
    test = CLAIMS[claim]["transcript"]
    by_video = {}
    for n in notes:
        result = test({f: n.get(f) for f in FIELDS + ("spoken_as",) if n.get(f)})
        if not result:
            continue
        entry = {"video_id": n["video_id"], "result": result, "time": n.get("time"), "note": n["text"],
                 "transcript_snippet": n.get("snippet"), "placed_by": n.get("assignment_method"),
                 "placement_confidence": n.get("confidence"),
                 "source": f"https://www.youtube.com/watch?v={n['video_id']}"}
        # A video that both confirms and contradicts counts as confirming only if nothing contradicts
        previous = by_video.get(n["video_id"])
        if previous is None or (previous["result"] == "confirm" and result == "contradict"):
            by_video[n["video_id"]] = entry
    return {"confirm": [e for e in by_video.values() if e["result"] == "confirm"],
            "contradict": [e for e in by_video.values() if e["result"] == "contradict"]}


def telemetry_evidence(claim, metrics, label):
    test = CLAIMS[claim]["telemetry"]
    if not test or not metrics or label not in metrics["turns"]:
        return None
    m = metrics["turns"][label]
    result = test(m)
    return {"result": result, "laps": m["laps"], "metrics": m} if result else {"result": None, "laps": m["laps"],
                                                                                 "metrics": m}


# --- layouts and identical corners ------------------------------------------------------------

class Layouts:
    def __init__(self):
        self.info = load_layouts()
        self.turns, self.xy, self.packs = {}, {}, {}
        for path in (GENERATED / "knowledge_packs").glob("*.json"):
            pack = json.loads(path.read_text(encoding="utf-8"))
            tid = pack["track_id"]
            turns, _ = clean_turns(pack)
            self.turns[tid] = turns
            kept = dict(turns)
            self.xy[tid] = {t["label"]: (t["x"], t["y"]) for t in pack.get("turns", [])
                            if kept.get(t["label"]) == t["lap_pct"]}
        self._metrics = {}

    def metrics(self, tid):
        if tid not in self._metrics:
            self._metrics[tid] = corner_metrics(tid, tuple(self.turns.get(tid, []))) if self.turns.get(tid) else None
        return self._metrics[tid]

    def siblings(self, tid):
        venue = self.info.get(tid, {}).get("venue")
        return [t for t, i in self.info.items() if venue and i["venue"] == venue and t != tid and t in self.xy]

    def match(self, a, label, b, config):
        """(label at b, inheritance confidence) for the corner of b on the same spot, or None."""
        if label not in self.xy.get(a, {}):
            return None
        x, y = self.xy[a][label]
        best = min(((math.dist((x, y), xy), l) for l, xy in self.xy[b].items()), default=None)
        if not best or best[0] > config["near_corner_px"]:
            return None
        conf = 1.0 if best[0] <= config["same_corner_px"] else config["near_confidence"]
        if self.info.get(a, {}).get("legacy") != self.info.get(b, {}).get("legacy"):
            conf = min(conf, config["legacy_confidence"])
        return best[1], conf

    def neighbours(self, tid, label):
        labels = [l for l, _ in self.turns.get(tid, [])]
        if label not in labels:
            return None, None
        i = labels.index(label)
        return labels[i - 1], labels[(i + 1) % len(labels)]

    def same_approach(self, a, label, b, label_b, config):
        """True when the corners before and after also sit on the same spots."""
        prev_a, next_a = self.neighbours(a, label)
        prev_b, next_b = self.neighbours(b, label_b)
        if not prev_a or not prev_b:
            return False
        pm, nm = self.match(a, prev_a, b, config), self.match(a, next_a, b, config)
        return bool(pm and nm and pm[0] == prev_b and nm[0] == next_b)


def direct_evidence(tid, label, claim, layouts, notes):
    return {"transcript": transcript_evidence(claim, notes.get((tid, label), [])),
            "telemetry": telemetry_evidence(claim, layouts.metrics(tid), label)}


def variant_evidence(tid, label, claim, layouts, notes, inherit):
    out = []
    for other in layouts.siblings(tid):
        found = layouts.match(tid, label, other, inherit)
        if not found:
            continue
        other_label, conf = found
        if CLAIMS[claim]["approach_dependent"] and not layouts.same_approach(tid, label, other, other_label, inherit):
            continue
        ev = direct_evidence(other, other_label, claim, layouts, notes)
        t = ev["transcript"]
        tel = (ev["telemetry"] or {}).get("result")
        result = "contradict" if tel == "contradict" or (t["contradict"] and not t["confirm"]) else \
            "confirm" if tel == "confirm" or t["confirm"] else None
        if result:
            out.append({"source_track": layouts.info.get(other, {}).get("name"), "source_track_id": other,
                        "corner": other_label, "inheritance_confidence": conf, "result": result,
                        "transcript_confirmations": len(t["confirm"]), "telemetry": tel})
    return out


# --- main -------------------------------------------------------------------------------------

def band(confidence, bands):
    return "high" if confidence >= bands["high"] else "medium" if confidence >= bands["medium"] else "low"


def main():
    config = load_config()
    inherit = config["inheritance"]
    layouts = Layouts()
    notes = transcript_notes()
    before = {tid: repo.load("validated", tid) for tid in repo.track_ids("validated")}
    validated_before = sum(len(r) for r in before.values())

    candidates = {tid: repo.load("candidates", tid) for tid in repo.track_ids("candidates")}
    validated, rejected = defaultdict(dict), defaultdict(dict)
    statuses, bands_count, by_claim = Counter(), Counter(), defaultdict(Counter)
    for tid, records in candidates.items():
        for rid, record in records.items():
            label, claim = record["corner"], record["claim"]
            if claim not in CLAIMS:
                continue
            ev = direct_evidence(tid, label, claim, layouts, notes)
            variants = variant_evidence(tid, label, claim, layouts, notes, inherit)
            scored = score({"research": record["research"], "transcript": ev["transcript"],
                            "telemetry": ev["telemetry"], "variants": variants}, config)
            previous = record.get("confidence_history") or []
            entry = {"at": repo.now(), "consensus": scored["confidence"]["consensus"], "status": scored["status"]}
            if not previous or (previous[-1]["consensus"], previous[-1]["status"]) != (entry["consensus"], entry["status"]):
                previous.append(entry)
            record.update({
                "status": scored["status"], "reason": scored["reason"], "confidence": scored["confidence"],
                "evidence": {"transcript": ev["transcript"], "telemetry": ev["telemetry"], "variants": variants},
                "counts": scored["counts"], "confidence_history": previous,
                "explanation": explain(record["statement"], label, scored),
            })
            statuses[scored["status"]] += 1
            by_claim[claim][scored["status"]] += 1
            if scored["status"] == "validated":
                validated[tid][rid] = {**record, "status": "approved", "basis": "consensus"}
                bands_count[band(scored["confidence"]["consensus"], config["bands"])] += 1
            elif scored["status"] == "rejected":
                rejected[tid][rid] = record
            else:
                bands_count[band(scored["confidence"]["consensus"], config["bands"])] += 1

    # Inheritance: copy claims validated by a layout's own evidence to identical corners elsewhere
    inherited = 0
    for tid, records in list(validated.items()):
        for rid, record in list(records.items()):
            if record.get("basis") != "consensus":
                continue  # inherited records added earlier in this loop are not re-inherited
            counts = record.get("counts", {})
            own_evidence = counts.get("telemetry") == "confirm" or counts.get("transcript_confirmations")
            if not own_evidence:
                continue  # only claims this layout's own transcripts or telemetry confirmed
            for other in layouts.siblings(tid):
                found = layouts.match(tid, record["corner"], other, inherit)
                if not found:
                    continue
                other_label, conf = found
                if CLAIMS[record["claim"]]["approach_dependent"] and \
                        not layouts.same_approach(tid, record["corner"], other, other_label, inherit):
                    continue
                confidence = round(record["confidence"]["consensus"] * conf, 3)
                target_id = repo.record_id(other, other_label, record["claim"])
                own = direct_evidence(other, other_label, record["claim"], layouts, notes)
                contradicted = (own["telemetry"] or {}).get("result") == "contradict" or own["transcript"]["contradict"]
                if target_id in validated[other] or target_id in rejected[other] or contradicted \
                        or confidence < inherit["min_confidence"] or conf < inherit["min_confidence"]:
                    continue
                validated[other][target_id] = {
                    "id": target_id, "track_id": other, "track": layouts.info.get(other, {}).get("name"),
                    "corner": other_label, "corner_name": None, "claim": record["claim"],
                    "statement": record["statement"], "status": "approved", "basis": "inherited",
                    "confidence": {"consensus": confidence}, "source_track": record["track"],
                    "source_track_id": tid, "source_corner": record["corner"], "inheritance_confidence": conf,
                    "evidence": {"inherited_from": rid}, "reason": "validated at an identical corner",
                    "explanation": f"{record['statement']} at {other_label}: inherited from {record['track']} "
                                   f"{record['corner']} (same corner{', same approach' if CLAIMS[record['claim']]['approach_dependent'] else ''}, "
                                   f"inheritance {conf:.2f}); {record['explanation']}",
                    "inherited_at": repo.now(),
                }
                inherited += 1

    for tid, records in candidates.items():
        repo.save("candidates", tid, next(iter(records.values()), {}).get("track"), records)
    for tid in set(before) | set(validated) | set(rejected) | set(candidates):
        name = layouts.info.get(tid, {}).get("name")
        repo.save("validated", tid, name, validated.get(tid, {}))
        repo.save("rejected", tid, name, rejected.get(tid, {}))

    validated_after = sum(len(r) for r in validated.values())
    new_ids = {rid for recs in validated.values() for rid in recs} - {rid for recs in before.values() for rid in recs}
    report = {
        "research_generated": {"tracks_researched": len(candidates),
                               "candidate_facts": sum(len(r) for r in candidates.values()),
                               "by_source": dict(Counter(s["source"].split(":")[0] for recs in candidates.values()
                                                         for r in recs.values() for s in r["research"]))},
        "validation_results": {"validated": statuses["validated"], "rejected": statuses["rejected"],
                               "pending": statuses["pending"], "inherited": inherited},
        "consensus_results": {f"{k}_confidence": bands_count[k] for k in ("high", "medium", "low")},
        "knowledge_growth": {"before": validated_before, "after": validated_after,
                             "new_validated_entries": len(new_ids)},
        "by_claim": {c: dict(v) for c, v in sorted(by_claim.items())},
        "evidence_used": {
            "transcript": sum(1 for recs in candidates.values() for r in recs.values()
                              if r.get("counts", {}).get("transcript_confirmations")),
            "telemetry": sum(1 for recs in candidates.values() for r in recs.values()
                             if r.get("counts", {}).get("telemetry") == "confirm"),
            "variants": sum(1 for recs in candidates.values() for r in recs.values()
                            if r.get("counts", {}).get("variant_confirmations"))},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
