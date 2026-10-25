"""Build start-aligned, race-direction centrelines and turn markers.

Inputs : generated/axes_normalized/<id>_axis.csv, start-finish.svg, turns.svg
Outputs: generated/centrelines/<id>.csv  (lap_pct,x,y in SVG 1920x1080 space)
         generated/turn_markers/<id>.json
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.geometry.centreline_alignment import align, load_axis, start_finish_point, turn_markers
from src.shared.paths import GENERATED, TRACK_MAPS

CENTRELINES = GENERATED / "centrelines"
MARKERS = GENERATED / "turn_markers"


def main():
    CENTRELINES.mkdir(exist_ok=True)
    MARKERS.mkdir(exist_ok=True)
    built = unknown = failed = 0

    for entry in json.loads((GENERATED / "track_catalog.json").read_text(encoding="utf-8")):
        track_id = entry["track_id"]
        folder = TRACK_MAPS / entry["layout_path"]
        axis_file = GENERATED / "axes_normalized" / f"{track_id}_axis.csv"
        sf_file = folder / "start-finish.svg"
        if not (axis_file.exists() and sf_file.exists()):
            continue
        try:
            axis = load_axis(axis_file)
            markers = turn_markers(folder / "turns.svg")
            line, turns, direction_known = align(axis, start_finish_point(sf_file, axis), markers)
        except Exception as ex:
            failed += 1
            print(track_id, "FAILED", ex)
            continue

        np.savetxt(CENTRELINES / f"{track_id}.csv", line, delimiter=",",
                   header="lap_pct,x,y", comments="", fmt=("%.5f", "%.2f", "%.2f"))
        (MARKERS / f"{track_id}.json").write_text(json.dumps(
            {"track_id": track_id, "direction_known": direction_known, "turns": turns}, indent=1),
            encoding="utf-8")
        built += 1
        unknown += not direction_known

    print(f"centrelines: {built}  direction unknown: {unknown}  failed: {failed}")


if __name__ == "__main__":
    main()
