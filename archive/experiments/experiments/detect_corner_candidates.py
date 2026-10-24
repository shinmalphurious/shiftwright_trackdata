from pathlib import Path
import json
import numpy as np
from scipy.signal import find_peaks

# Load curvature generated previously
data = np.loadtxt(
    "experiments/spielberg_curvature_values.csv",
    delimiter=","
)

lap_pct = data[:,0]
curvature = data[:,1]

peaks, props = find_peaks(
    curvature,
    prominence=0.01,
    distance=50
)

results = []

for idx in peaks:

    results.append({
        "lap_pct":
            round(
                float(
                    lap_pct[idx]
                ),
                4
            ),

        "curvature":
            round(
                float(
                    curvature[idx]
                ),
                6
            )
    })

print()

for result in results:

    print(result)

with open(
    "experiments/spielberg_corner_candidates.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        results,
        fp,
        indent=2
    )

print()
print(
    "Saved:"
    " experiments/spielberg_corner_candidates.json"
)
