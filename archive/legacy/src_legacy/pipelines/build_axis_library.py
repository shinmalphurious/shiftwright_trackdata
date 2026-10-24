from pathlib import Path

import numpy as np

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT)
)

from src.geometry.skeleton_generator import svg_to_skeleton
from src.geometry.centreline_extractor import (
    skeleton_to_points,
    order_skeleton
)

VECTOR_ROOT = Path(
r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing"
)

OUTPUT = Path(
    "generated/axes"
)

OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)

built = 0

for svg in VECTOR_ROOT.rglob(
    "active.svg"
):

    track_folder = svg.parent.name

    track_id = track_folder.split(
        "-"
    )[0]

    try:

        skeleton = svg_to_skeleton(
            svg
        )

        points = skeleton_to_points(
            skeleton
        )

        ordered = order_skeleton(
            points
        )

        np.savetxt(
            OUTPUT /
            f"{track_id}_axis.csv",
            ordered,
            delimiter=",",
            fmt="%d"
        )

        built += 1

        print(
            f"{track_id} OK"
        )

    except Exception as ex:

        print(
            f"{track_id} FAIL {ex}"
        )

print()
print(
    f"Built: {built}"
)
