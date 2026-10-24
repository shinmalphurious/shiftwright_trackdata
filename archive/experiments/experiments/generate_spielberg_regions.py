import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT)
)

import numpy as np
import json

from src.corners.curvature_peak_detector import (
    detect_corner_candidates
)

from src.corners.corner_region_detector import (
    expand_corner_region
)

AXIS_FILE = Path(
    "generated/axes_normalized/403_axis.csv"
)

data = np.loadtxt(
    AXIS_FILE,
    delimiter=",",
    skiprows=1
)

peaks, curvature = detect_corner_candidates(
    data
)

corners = []

for peak in peaks:

    start, apex, end = expand_corner_region(
        curvature,
        peak
    )

    corners.append({

        "start_pct":
            round(
                float(
                    data[start][0]
                ),
                6
            ),

        "apex_pct":
            round(
                float(
                    data[apex][0]
                ),
                6
            ),

        "end_pct":
            round(
                float(
                    data[end][0]
                ),
                6
            ),

        "strength":
            round(
                float(
                    curvature[
                        apex
                    ]
                ),
                6
            )
    })

with open(
    "generated/403_generated_corners.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        corners,
        fp,
        indent=2
    )

print()
print(
    f"Corners: {len(corners)}"
)

print()
print(
    "generated/403_generated_corners.json"
)
