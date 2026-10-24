import sys
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT)
)

from src.corners.curvature_peak_detector import (
    detect_corner_candidates
)

from src.corners.corner_region_detector import (
    expand_corner_region
)

from src.corners.region_deduplicator import (
    deduplicate_regions
)

AXIS_DIR = Path(
    "generated/axes_normalized"
)

OUTPUT_DIR = Path(
    "generated/corner_regions"
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

        peaks, curvature = (
            detect_corner_candidates(
                data
            )
        )

        corners = []

        for peak in peaks:

            start, apex, end = (
                expand_corner_region(
                    curvature,
                    peak
                )
            )

            corners.append(
                {
                    "start_pct": round(
                        float(data[start][0]),
                        6
                    ),
                    "apex_pct": round(
                        float(data[apex][0]),
                        6
                    ),
                    "end_pct": round(
                        float(data[end][0]),
                        6
                    ),
                    "strength": round(
                        float(curvature[apex]),
                        6
                    )
                }
            )

        corners = deduplicate_regions(
            corners
        )

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

                    "corner_count":
                        len(corners),

                    "corners":
                        corners
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
            f"{track_id} FAIL: {ex}"
        )

print()
print(
    f"Built: {built}"
)
