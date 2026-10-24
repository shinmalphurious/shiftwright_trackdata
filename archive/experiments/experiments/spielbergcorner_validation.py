from pathlib import Path
from svgpathtools import svg2paths

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
import json

SVG_FILE = Path(
r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing\Road\spielberg\403-spielberg-gp\active.svg"
)

paths,_ = svg2paths(
    str(SVG_FILE)
)

path = paths[0]

N = 8000

pts = []

for i in range(N):

    p = path.point(
        i/(N-1)
    )

    pts.append([
        p.real,
        p.imag
    ])

pts = np.array(
    pts
)

#
# TOPOLOGY SOLVED FROM EXPERIMENTS
#

split = 4052

outer = pts[:split]
inner = pts[split:]

#
# CREATE WALL PAIRS
#

tree = KDTree(
    inner
)

centre = []

for p in outer:

    _, idx = tree.query(
        p
    )

    q = inner[idx]

    centre.append(
        (p + q) / 2
    )

centre = np.array(
    centre
)

#
# SMOOTH CENTRELINE
#

x = gaussian_filter1d(
    centre[:,0],
    sigma=5
)

y = gaussian_filter1d(
    centre[:,1],
    sigma=5
)

centre = np.column_stack(
    (
        x,
        y
    )
)

#
# CURVATURE
#

dx = np.gradient(
    centre[:,0]
)

dy = np.gradient(
    centre[:,1]
)

ddx = np.gradient(
    dx
)

ddy = np.gradient(
    dy
)

num = np.abs(
    dx * ddy
    -
    dy * ddx
)

den = np.power(
    dx*dx + dy*dy,
    1.5
)

curvature = np.divide(
    num,
    den,
    out=np.zeros_like(num),
    where=den>0
)

curvature = gaussian_filter1d(
    curvature,
    sigma=10
)

lap_pct = np.linspace(
    0,
    1,
    len(curvature)
)

#
# REMOVE SEAM REGION
#

mask = (
    (lap_pct > 0.02)
    &
    (lap_pct < 0.98)
)

curvature_clean = curvature.copy()

curvature_clean[
    ~mask
] = 0

#
# PEAK DETECTION
#

peaks, props = find_peaks(
    curvature_clean,
    prominence=0.01,
    distance=100
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

#
# OUTPUT JSON
#

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

#
# OUTPUT CSV
#

np.savetxt(
    "experiments/spielberg_curvature_values.csv",
    np.column_stack(
        (
            lap_pct,
            curvature
        )
    ),
    delimiter=","
)

#
# PLOT
#

plt.figure(
    figsize=(14,5)
)

plt.plot(
    lap_pct,
    curvature,
    linewidth=2,
    label="Curvature"
)

for peak in peaks:

    plt.scatter(
        lap_pct[peak],
        curvature[peak],
        s=60,
        color="red"
    )

# Lovely references

for marker in [
    0.075,
    0.290,
    0.470,
    0.590,
    0.675,
    0.830,
    0.905
\]:

    plt.axvline(
        marker,
        linestyle="--",
        alpha=0.3
    )

plt.title(
    "Spielberg Corner Candidate Validation"
)

plt.xlabel(
    "Lap Percentage"
)

plt.ylabel(
    "Curvature"
)

plt.legend()

plt.savefig(
    "experiments/spielberg_corner_validation.png",
    dpi=200,
    bbox_inches="tight"
)

print()
print(
    "Detected Peaks"
)

for r in results:

    print(r)

print()
print(
    "Saved:"
)

print(
    "experiments/spielberg_corner_candidates.json"
)

print(
    "experiments/spielberg_corner_validation.png"
)

print(
    "experiments/spielberg_curvature_values.csv"
)
