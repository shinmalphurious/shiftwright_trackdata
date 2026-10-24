import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT)
)

import json
import numpy as np

AXIS_DIR = Path(
    "generated/axes_normalized"
)

CORNER_DIR = Path(
    "generated/corner_regions"
)

OUTPUT_DIR = Path(
    "generated/corner_metrics"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

built = 0

for corner_file in CORNER_DIR.glob(
    "*.json"
):

    track_id = corner_file.stem

    axis_file = (
        AXIS_DIR /
        f"{track_id}_axis.csv"
    )

    if not axis_file.exists():
        continue

    axis = np.loadtxt(
        axis_file,
        delimiter=",",
        skiprows=1
    )

    data = json.load(
        open(
            corner_file,
            encoding="utf-8"
        )
    )

    metrics = []

    for corner in data[
        "corners"
    ]:

        start_pct = corner[
            "start_pct"
        ]

        apex_pct = corner[
            "apex_pct"
        ]

        end_pct = corner[
            "end_pct"
        ]

        width_pct = (
            end_pct
            -
            start_pct
        )

        start_idx = int(
            start_pct
            *
            (
                len(axis)-1
            )
        )

        apex_idx = int(
            apex_pct
            *
            (
                len(axis)-1
            )
        )

        end_idx = int(
            end_pct
            *
            (
                len(axis)-1
            )
        )

        p1 = axis[
            start_idx
        ][1:3]

        p2 = axis[
            apex_idx
        ][1:3]

        p3 = axis[
            end_idx
        ][1:3]

        v1 = p2 - p1
        v2 = p3 - p2

        angle = np.degrees(
            np.arccos(
                np.clip(
                    np.dot(
                        v1,
                        v2
                    )
                    /
                    (
                        np.linalg.norm(v1)
                        *
                        np.linalg.norm(v2)
                    ),
                    -1,
                    1
                )
            )
        )

        metrics.append({

            "start_pct":
                start_pct,

            "apex_pct":
                apex_pct,

            "end_pct":
                end_pct,

            "strength":
                corner[
                    "strength"
                ],

            "width_pct":
                round(
                    width_pct,
                    6
                ),

            "angle_deg":
                round(
                    float(angle),
                    2
                )
        })

    with open(
        OUTPUT_DIR /
        corner_file.name,
        "w",
        encoding="utf-8"
    ) as fp:

        json.dump(
            {
                "track_id":
                    int(track_id),

                "corners":
                    metrics
            },
            fp,
            indent=2
        )

    built += 1

print()
print(
    f"Built: {built}"
)
