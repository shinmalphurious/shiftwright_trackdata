from pathlib import Path
from svgpathtools import svg2paths

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

SVG_FILE = Path(
r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing\Road\spielberg\403-spielberg-gp\active.svg"
)

paths, _ = svg2paths(
    str(SVG_FILE)
)

path = paths[0]

N = 5000

pts = []

for i in range(N):

    p = path.point(
        i/(N-1)
    )

    pts.append(
        [
            p.real,
            p.imag
        ]
    )

pts = np.array(pts)

half = len(pts)//2

outer = pts[:half]
inner = pts[half:]

tree = KDTree(inner)

centre = []

widths = []

for point in outer:

    distance, idx = tree.query(
        point
    )

    inner_point = inner[idx]

    midpoint = (
        point + inner_point
    ) / 2

    centre.append(
        midpoint
    )

    widths.append(
        distance
    )

centre = np.array(
    centre
)

plt.figure(
    figsize=(12,8)
)

plt.plot(
    outer[:,0],
    outer[:,1],
    linewidth=1,
    label="Outer"
)

plt.plot(
    inner[:,0],
    inner[:,1],
    linewidth=1,
    label="Inner"
)

plt.scatter(
    centre[:,0],
    centre[:,1],
    s=2,
    label="Medial Candidates"
)

plt.gca().set_aspect(
    "equal"
)

plt.legend()

plt.title(
    "Spielberg Medial Axis Experiment"
)

plt.savefig(
    "experiments/spielberg_medial_axis.png",
    dpi=200,
    bbox_inches="tight"
)

print()
print(
    f"Average width: "
    f"{np.mean(widths):.2f}"
)

print(
    f"Min width: "
    f"{np.min(widths):.2f}"
)

print(
    f"Max width: "
    f"{np.max(widths):.2f}"
)

print()
print(
    "Saved:"
    " experiments/spielberg_medial_axis.png"
)
