import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT)
)

import json
import numpy as np

from src.corners.curvature_peak_detector import (
    detect_corner_candidates
)

from src.corners.corner_region_detector import (
    expand_corner_region
)

axis = np.loadtxt(
    "generated/axes_normalized/403_axis.csv",
    delimiter=",",
    skiprows=1
)

peaks, curvature = detect_corner_candidates(
    axis
)

regions = []

for peak in peaks:

    start, apex, end = expand_corner_region(
        curvature,
        peak
    )

    regions.append({

        "start_pct":
            round(
                float(
                    axis[start][0]
                ),
                6
            ),

        "apex_pct":
            round(
                float(
                    axis[apex][0]
                ),
                6
            ),

        "end_pct":
            round(
                float(
                    axis[end][0]
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
    "generated/403_corner_regions.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        regions,
        fp,
        indent=2
    )

print()
print(
    f"Regions: {len(regions)}"
)

print()

for region in regions:

    print(region)

print()

print(
    "Saved:"
)

print(
    "generated/403_corner_regions.json"
)
