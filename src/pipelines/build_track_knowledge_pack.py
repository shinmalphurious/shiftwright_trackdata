"""Final step: one knowledge pack per track, consumed by the Shiftwright platform.

Pack schema (stable contract, see docs/KNOWLEDGE_PACK.md):
  track_id, knowledge_level ("named" | "geometry_only"), metadata {name, length_m},
  turns [{label, number, x, y, lap_pct}], direction_known,
  named_corners [{name, start_pct, end_pct, labels[...], ...}],
  generated_corner_regions, youtube_summary, turn_consensus
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared.paths import GENERATED

OUTDIR = GENERATED / "knowledge_packs"


def _load(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def corner_facts(track_id):
    """{label: [{claim, statement, confidence, basis, evidence, source_track?}]} from the validated
    repository."""
    records = _load(GENERATED / "knowledge" / "validated" / f"{track_id}.json", {}).get("records", {})
    facts = {}
    for r in records.values():
        if r.get("status") != "approved":
            continue
        counts = r.get("counts") or {}
        fact = {"claim": r["claim"], "statement": r["statement"],
                "confidence": r["confidence"]["consensus"], "basis": r.get("basis"),
                "evidence": {"research": counts.get("research_sources", 0),
                             "transcript": counts.get("transcript_confirmations", 0),
                             "telemetry_laps": counts.get("telemetry_laps", 0) if counts.get("telemetry") == "confirm" else 0,
                             "variants": counts.get("variant_confirmations", 0)},
                "explanation": r.get("explanation")}
        if r.get("basis") == "inherited":
            fact.update(source_track=r["source_track"], source_corner=r["source_corner"],
                        inheritance_confidence=r["inheritance_confidence"])
        facts.setdefault(r["corner"], []).append(fact)
    return facts


def main():
    # Warnings about the source data (duplicate turn ids, gaps, alias clashes); they do not stop the build
    from src.pipelines.validate_track_knowledge import run as validate
    validate()
    OUTDIR.mkdir(exist_ok=True)
    built = 0
    checks = _load(GENERATED / "axes" / "axis_quality.json", {})
    for source in GENERATED.glob("*.json"):
        if not source.stem.isdigit():
            continue
        track_id = int(source.stem)
        track = _load(source, {})
        youtube = _load(GENERATED / "youtube_knowledge" / f"{track_id}.json", {})
        markers = _load(GENERATED / "turn_markers" / f"{track_id}.json", {})
        turns = markers.get("turns", [])
        direction_known = markers.get("direction_known", False)

        named = []
        for corner in track.get("corners", []):
            start, end = corner.get("start_pct"), corner.get("end_pct")
            labels = [t["label"] for t in turns
                      if direction_known and start is not None and end is not None
                      and start <= t["lap_pct"] <= end]
            named.append({**corner, "labels": labels})

        pack = {
            "track_id": track_id,
            "knowledge_level": "named" if named else "geometry_only",
            "metadata": track.get("metadata", {}),
            "direction_known": direction_known,
            # Centreline check against the active.svg ribbon (src/geometry/ribbon_axis.py); ok false =
            # the centreline is approximate for this layout
            "centreline_check": checks.get(str(track_id)),
            "turns": turns,
            "named_corners": named,
            "generated_corner_regions": _load(GENERATED / "corner_regions" / f"{track_id}.json", {}).get("corners", []),
            "youtube_summary": youtube.get("track_summary", {}),
            "turn_consensus": youtube.get("turn_consensus", {}),
            # Per-turn driving instructions from lap-guide videos (build_corner_guidance)
            "corner_guidance": _load(GENERATED / "corner_guidance" / f"{track_id}.json", {}).get("corners", {}),
            # Consensus-approved facts only (generated/knowledge/validated, the source of truth);
            # research candidates never reach the pack
            "corner_facts": corner_facts(track_id),
        }
        (OUTDIR / f"{track_id}.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
        built += 1

    print("knowledge packs:", built)


if __name__ == "__main__":
    main()
