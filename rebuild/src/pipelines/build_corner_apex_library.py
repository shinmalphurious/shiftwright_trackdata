import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT)
)

import json
import numpy as np

from src.corners.curvature_peak_detector import (
    detect_corner_candidates
)

AXIS_DIR = Path(
    "generated/axes_normalized"
)

OUTPUT_DIR = Path(
    "generated/corner_apexes"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

built = 0

for axis_file in AXIS_DIR.glob(
    "*_axis.csv"
):

    track_id = (
        axis_file.stem
        .replace(
            "_axis",
            ""
        )
    )

    try:

        data = np.loadtxt(
            axis_file,
            delimiter=",",
            skiprows=1
        )

        peaks, curvature = detect_corner_candidates(
            data
        )

        apexes = []

        for peak in peaks:

            apexes.append({

                "lap_pct":
                    round(
                        float(
                            data[peak][0]
                        ),
                        6
                    ),

                "curvature":
                    round(
                        float(
                            curvature[peak]
                        ),
                        6
                    )
            })

        with open(
            OUTPUT_DIR /
            f"{track_id}.json",
            "w",
            encoding="utf-8"
        ) as fp:

            json.dump(
                {
                    "track_id":
                        int(track_id),

                    "source":
                        "generated",

                    "apex_count":
                        len(apexes),

                    "apexes":
                        apexes
                },
                fp,
                indent=2
            )

        built += 1

        if built % 25 == 0:

            print(
                f"{built} complete"
            )

    except Exception as ex:

        print(
            f"{track_id} FAIL: "
            f"{ex}"
        )

print()

print(
    f"Built: {built}"
)
