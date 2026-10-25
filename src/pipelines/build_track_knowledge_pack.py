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


def main():
    OUTDIR.mkdir(exist_ok=True)
    built = 0
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
            "turns": turns,
            "named_corners": named,
            "generated_corner_regions": _load(GENERATED / "corner_regions" / f"{track_id}.json", {}).get("corners", []),
            "youtube_summary": youtube.get("track_summary", {}),
            "turn_consensus": youtube.get("turn_consensus", {}),
        }
        (OUTDIR / f"{track_id}.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
        built += 1

    print("knowledge packs:", built)


if __name__ == "__main__":
    main()
