"""Tier 1, research: propose candidate claims about each corner. Nothing here is authoritative.

Sources (each recorded per claim, so independent sources can be counted):
    geometry          deterministic rules on the centreline: a long run into a corner suggests heavy
                      braking and an overtaking spot, a long run after it an important exit.
    ai:<model>        a local Ollama model proposes claims from the official iRacing description
                      (used only when it names the venue: about a third of the stored descriptions
                      belong to another track) and the corner list with its geometry. Its
                      confidence is capped at research_prior_cap.
Claims must come from src/knowledge/claims.py. Labels must be turns of the layout.

Writes generated/knowledge/candidates/<track_id>.json (merging with what is there: a source's
earlier proposals are replaced, other sources and the validation history are kept).

Usage:
    python -m src.pipelines.research_track_candidates                layouts with guidance or telemetry
    python -m src.pipelines.research_track_candidates --track 485 --no-ai
    python -m src.pipelines.research_track_candidates --all
Then run validate_knowledge_candidates.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.knowledge import repository as repo
from src.knowledge.claims import CLAIMS
from src.knowledge.consensus import load_config
from src.pipelines.enrich_corner_assignments import clean_turns
from src.shared import ollama
from src.shared.iracing_tracks import load_layouts, venue_record
from src.shared.paths import GENERATED
from src.shared.track_names import normalize
from src.shared.telemetry_landmarks import coverage

LONG_RUN_M = 600
GEOMETRY = "geometry"

SYSTEM = """You help build a race track knowledge base. You propose HYPOTHESES about corners; \
they will be checked against driver commentary and telemetry before anyone relies on them, and \
wrong ones will be rejected. Only propose a claim when you have a real basis (the description, \
the distances given, or well-known facts about this circuit). Use only the claim names listed. \
research_confidence: how sure you are, 0 to 1. basis: a few words on why."""

SCHEMA = {
    "type": "object", "required": ["corners"],
    "properties": {"corners": {"type": "array", "items": {
        "type": "object", "required": ["label", "claims"],
        "properties": {
            "label": {"type": "string"},
            "claims": {"type": "array", "items": {
                "type": "object", "required": ["claim", "research_confidence", "basis"],
                "properties": {"claim": {"type": "string", "enum": sorted(CLAIMS)},
                               "research_confidence": {"type": "number"},
                               "basis": {"type": "string"}}}},
        }}}},
}


def description(track_id):
    """The official description, only when it is about this venue."""
    layouts = load_layouts()
    venue = layouts.get(track_id, {}).get("venue", "")
    text = (venue_record(venue) or {}).get("about_text") or ""
    words = [w for w in normalize(venue).split() if len(w) >= 5
             and w not in ("circuit", "raceway", "speedway", "international", "motor", "course", "street")]
    return text if words and any(w in normalize(text) for w in words) else None


def corner_table(track_id, pack):
    """[{label, name, lap_pct, run_before_m, run_after_m, angle_deg}] in lap order."""
    turns, _ = clean_turns(pack)
    length = (pack.get("metadata") or {}).get("length_m")
    names = {l: c["name"] for c in pack.get("named_corners", []) for l in dict.fromkeys(c.get("labels", []))
             if c.get("name") and len(set(c.get("labels", []))) == 1}
    regions_path = GENERATED / "corner_characteristics" / f"{track_id}.json"
    regions = json.loads(regions_path.read_text(encoding="utf-8")).get("corners", []) if regions_path.exists() else []
    rows = []
    for i, (label, p) in enumerate(turns):
        before = (p - turns[i - 1][1]) % 1.0 if len(turns) > 1 else None
        after = (turns[(i + 1) % len(turns)][1] - p) % 1.0 if len(turns) > 1 else None
        region = min(regions, key=lambda r: abs(r["apex_pct"] - p), default=None)
        if region and abs(region["apex_pct"] - p) > 0.03:
            region = None
        rows.append({"label": label, "name": names.get(label), "lap_pct": round(p, 4),
                     "run_before_m": round(before * length) if length and before is not None else None,
                     "run_after_m": round(after * length) if length and after is not None else None,
                     "angle_deg": region.get("angle_deg") if region else None})
    return rows


def geometry_claims(rows):
    out = []
    for r in rows:
        add = lambda claim, conf, basis: out.append((r["label"], claim, conf, basis))
        if r["run_before_m"] and r["run_before_m"] >= LONG_RUN_M:
            add("heavy_braking", 0.6, f"{r['run_before_m']} m from the previous corner")
            add("overtaking_zone", 0.45, f"{r['run_before_m']} m from the previous corner")
        if r["run_after_m"] and r["run_after_m"] >= LONG_RUN_M:
            add("important_exit", 0.6, f"{r['run_after_m']} m to the next corner")
        # Turn angles from corner_characteristics are not used: they are smoothed curvature, not
        # the corner's real angle (Zandvoort's Tarzan hairpin measures 59 degrees, Hugenholtz 4)
    return out


def ai_claims(track_id, rows, model, cap):
    info = load_layouts().get(track_id, {})
    about = description(track_id)
    table = "\n".join(
        f"{r['label']}" + (f" ({r['name']})" if r["name"] else "")
        + f": lap position {r['lap_pct']:.2f}"
        + (f", {r['run_before_m']} m from previous corner" if r["run_before_m"] is not None else "")
        + (f", {r['run_after_m']} m to next corner" if r["run_after_m"] is not None else "")
        for r in rows)
    claims_text = "\n".join(f"- {name}: {spec['statement']}" for name, spec in CLAIMS.items())
    user = (f"Track: {info.get('name', track_id)}\n"
            + (f"Official description: {about[:2500]}\n" if about else "")
            + f"\nCorners in lap order:\n{table}\n\nClaim names you may use:\n{claims_text}\n\n"
            "For each corner, propose the claims you have a basis for (often none or one or two).")
    reply = ollama.chat_json(SYSTEM, user, SCHEMA, model=model, num_ctx=8192)
    labels = {r["label"] for r in rows}
    out = []
    for corner in reply.get("corners", []):
        m = re.search(r"\d+", corner.get("label", ""))
        label = f"T{int(m.group())}" if m else None
        if label not in labels:
            continue
        for c in corner.get("claims", []):
            if c.get("claim") in CLAIMS:
                conf = max(0.0, min(float(c.get("research_confidence") or 0), cap))
                out.append((label, c["claim"], round(conf, 2), (c.get("basis") or "")[:200]))
    return out, bool(about)


def targets(args):
    if args.track:
        return args.track
    packs = sorted(int(p.stem) for p in (GENERATED / "knowledge_packs").glob("*.json"))
    if args.all:
        return packs
    guided = {int(p.stem) for p in (GENERATED / "corner_guidance").glob("*.json") if p.stem.isdigit()}
    return [t for t in packs if t in guided or t in coverage()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--track", type=int, action="append")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--no-ai", action="store_true")
    parser.add_argument("--model", default=ollama.MODEL)
    args = parser.parse_args()
    cap = load_config()["research_prior_cap"]
    use_ai = not args.no_ai
    if use_ai:
        try:
            if args.model not in ollama.available_models():
                print(f"Ollama has no model {args.model}; geometry research only")
                use_ai = False
        except ollama.OllamaError as ex:
            print(f"{ex}; geometry research only")
            use_ai = False
    ai_source = f"ai:{args.model}"
    layouts = load_layouts()
    total = 0
    for track_id in targets(args):
        pack_path = GENERATED / "knowledge_packs" / f"{track_id}.json"
        if not pack_path.exists():
            continue
        pack = json.loads(pack_path.read_text(encoding="utf-8"))
        rows = corner_table(track_id, pack)
        if not rows:
            continue
        proposals = [(l, c, conf, basis, GEOMETRY) for l, c, conf, basis in geometry_claims(rows)]
        described = False
        if use_ai:
            try:
                found, described = ai_claims(track_id, rows, args.model, cap)
                proposals += [(l, c, conf, basis, ai_source) for l, c, conf, basis in found]
            except ollama.OllamaError as ex:
                print(f"  {track_id}: AI research failed ({ex}); geometry only")

        records = repo.load("candidates", track_id)
        names = {r["label"]: r["name"] for r in rows}
        sources_run = {GEOMETRY} | ({ai_source} if use_ai else set())
        for record in records.values():  # a source's earlier proposals are replaced by this run's
            record["research"] = [r for r in record.get("research", []) if r["source"] not in sources_run]
        for label, claim, conf, basis, source in proposals:
            rid = repo.record_id(track_id, label, claim)
            record = records.setdefault(rid, {
                "id": rid, "track_id": track_id, "track": layouts.get(track_id, {}).get("name"),
                "corner": label, "corner_name": names.get(label), "claim": claim,
                "statement": CLAIMS[claim]["statement"], "status": "candidate", "research": [],
                "confidence_history": [], "created_at": repo.now()})
            if not any(r["source"] == source for r in record["research"]):
                record["research"].append({"source": source, "confidence": conf, "basis": basis, "at": repo.now()})
        records = {rid: r for rid, r in records.items() if r.get("research")}
        repo.save("candidates", track_id, layouts.get(track_id, {}).get("name"), records)
        total += len(records)
        by_source = {}
        for _, _, _, _, source in proposals:
            by_source[source] = by_source.get(source, 0) + 1
        print(f"{track_id} {layouts.get(track_id, {}).get('name', '')}: {len(records)} candidates "
              f"{by_source}" + (" (description used)" if described else ""), flush=True)
    print(f"candidate claims: {total}")


if __name__ == "__main__":
    main()
