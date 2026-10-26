"""Build the track axis (ribbon centre, one closed loop) for every layout's active.svg.

Output: generated/axes/<track_id>_axis.csv (x,y per point, in order around the loop) and
generated/axes/axis_quality.json (per track: method, off-track share, coverage).

Method: src/geometry/ribbon_axis.py (even-odd ribbon fill, spur pruning, heading-following loop
trace, smoothing). Replaced the earlier joined-outline fill and nearest-neighbour ordering on
2026-10-26: that drew chords across the infield on about 180 of 408 layouts (e.g. Spa, Snetterton).
A layout whose new axis fails the quality check keeps its previous axis and is flagged.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.geometry.ribbon_axis import ribbon_axis  # noqa: E402
from src.shared.paths import GENERATED, TRACK_MAPS  # noqa: E402

OUTPUT = GENERATED / "axes"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    quality, built, kept, failed = {}, 0, 0, 0
    for svg in sorted(TRACK_MAPS.rglob("active.svg")):
        track_id = svg.parent.name.split("-")[0]
        if not track_id.isdigit():
            continue
        target = OUTPUT / f"{track_id}_axis.csv"
        try:
            axis, q = ribbon_axis(svg)
        except Exception as ex:                       # keep the previous axis, flag the layout
            q = {"ok": False, "error": str(ex)}
            axis = None
        if axis is not None and q["ok"]:
            np.savetxt(target, axis, delimiter=",", fmt="%.2f")
            built += 1
            method = "ribbon_axis"
        elif target.exists():
            kept += 1
            method = "previous (new axis failed the check)"
        else:
            failed += 1
            method = "none"
        quality[track_id] = {"method": method, **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in q.items()}}
        print(track_id, method, q)
    (OUTPUT / "axis_quality.json").write_text(json.dumps(quality, indent=1), encoding="utf-8")
    print(f"\nbuilt {built}, kept previous {kept}, failed {failed}")


if __name__ == "__main__":
    main()
