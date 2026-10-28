"""Which layouts have corner guidance, which have telemetry, and where telemetry would help most.

Telemetry (the driver's own laps in shiftwright.db, or reference laps under
$SHIFTWRIGHT_DATA_ROOT/references/<car>/<track_id>/*.csv) lets enrich_corner_assignments match
"next braking zone" notes to the corners where real laps brake. It is picked up automatically
on the next enrichment run; nothing else needs changing.

Writes generated/telemetry/telemetry_coverage.json:
    layouts[]            {track_id, track, guidance_available, guidance_corners, videos,
                          telemetry_available, telemetry_laps, reference_lap_available,
                          reference_laps, eligible, unassigned_notes, telemetry_resolvable_notes}
    acquisition_priority guidance layouts without telemetry, best value first:
                          {track_id, track, unassigned_notes, telemetry_resolvable_notes,
                           telemetry_value_score}
    transcript_priority  layouts with telemetry but no guidance yet (worth downloading guides for)
telemetry_resolvable_notes are unassigned notes about braking that lie between two placed
corners with corners in between: exactly what telemetry matching decides.

Usage: python -m src.pipelines.build_telemetry_coverage   (after enrich_corner_assignments)
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared.iracing_tracks import load_layouts
from src.shared.paths import GENERATED
from src.shared.telemetry_landmarks import coverage

OUT = GENERATED / "telemetry" / "telemetry_coverage.json"
GUIDANCE = GENERATED / "corner_guidance"
WEIGHTS = {"resolvable": 0.5, "unassigned": 0.3, "videos": 0.2}


def main():
    layouts = load_layouts()
    telemetry = coverage()
    unassigned, resolvable = Counter(), Counter()
    for path in (GUIDANCE / "enriched").glob("*.json"):
        result = json.loads(path.read_text(encoding="utf-8"))
        for n in result["notes"]:
            if n.get("corner_id"):
                continue
            unassigned[result["track_id"]] += 1
            if n.get("braking") and (n.get("unresolved") or {}).get("corners_between"):
                resolvable[result["track_id"]] += 1

    rows = []
    for pack in sorted((GENERATED / "knowledge_packs").glob("*.json"), key=lambda p: int(p.stem)):
        track_id = int(pack.stem)
        guide_path = GUIDANCE / f"{track_id}.json"
        guide = json.loads(guide_path.read_text(encoding="utf-8")) if guide_path.exists() else {}
        t = telemetry.get(track_id, {"laps": 0, "references": 0})
        row = {
            "track_id": track_id, "track": layouts.get(track_id, {}).get("name", str(track_id)),
            "guidance_available": bool(guide.get("corners")), "guidance_corners": len(guide.get("corners", {})),
            "videos": guide.get("videos", 0),
            "telemetry_available": t["laps"] > 0, "telemetry_laps": t["laps"],
            "reference_lap_available": t["references"] > 0, "reference_laps": t["references"],
            "unassigned_notes": unassigned[track_id], "telemetry_resolvable_notes": resolvable[track_id],
        }
        row["eligible"] = row["guidance_available"] and (row["telemetry_available"] or row["reference_lap_available"])
        rows.append(row)

    wanting = [r for r in rows if r["guidance_available"] and not r["eligible"]]
    top = {k: max((r[f] for r in wanting), default=0) or 1
           for k, f in (("resolvable", "telemetry_resolvable_notes"), ("unassigned", "unassigned_notes"),
                        ("videos", "videos"))}
    priority = sorted(({
        "track_id": r["track_id"], "track": r["track"], "unassigned_notes": r["unassigned_notes"],
        "telemetry_resolvable_notes": r["telemetry_resolvable_notes"], "videos": r["videos"],
        "telemetry_value_score": round(WEIGHTS["resolvable"] * r["telemetry_resolvable_notes"] / top["resolvable"]
                                       + WEIGHTS["unassigned"] * r["unassigned_notes"] / top["unassigned"]
                                       + WEIGHTS["videos"] * r["videos"] / top["videos"], 2),
    } for r in wanting), key=lambda r: -r["telemetry_value_score"])
    transcripts = [{"track_id": r["track_id"], "track": r["track"], "telemetry_laps": r["telemetry_laps"],
                    "reference_laps": r["reference_laps"]}
                   for r in rows if not r["guidance_available"] and (r["telemetry_available"] or r["reference_lap_available"])]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"layouts": rows, "acquisition_priority": priority,
                               "transcript_priority": transcripts, "weights": WEIGHTS}, indent=2,
                              ensure_ascii=False), encoding="utf-8")

    shown = [r for r in rows if r["guidance_available"] or r["telemetry_available"] or r["reference_lap_available"]]
    yes = lambda b: "Yes" if b else "No"
    print(f"{'Track':48} {'Guidance':>8} {'Telemetry':>9} {'Reference':>9} {'Eligible':>8}")
    print("-" * 86)
    for r in shown:
        print(f"{r['track'][:48]:48} {yes(r['guidance_available']):>8} {yes(r['telemetry_available']):>9} "
              f"{yes(r['reference_lap_available']):>9} {yes(r['eligible']):>8}")
    eligible = sum(r["eligible"] for r in rows)
    print(f"\nlayouts with guidance: {sum(r['guidance_available'] for r in rows)}, with telemetry or reference "
          f"laps: {sum(r['telemetry_available'] or r['reference_lap_available'] for r in rows)}, eligible: {eligible}")
    print("\nTelemetry acquisition priority (guidance, no telemetry):")
    for r in priority:
        print(f"  {r['telemetry_value_score']:.2f}  {r['track'][:48]:48} unassigned {r['unassigned_notes']:3}  "
              f"telemetry-resolvable {r['telemetry_resolvable_notes']:3}")
    print("\nTranscript priority (telemetry, no guidance yet):")
    for r in transcripts:
        print(f"  {r['track'][:48]:48} own laps {r['telemetry_laps']:3}  reference laps {r['reference_laps']}")


if __name__ == "__main__":
    main()
