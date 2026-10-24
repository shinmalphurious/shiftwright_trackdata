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

# Find seam

tree = KDTree(
    pts
)

best = None

for i in range(N):

    dists, idxs = tree.query(
        pts[i],
        k=20
    )

    for d, j in zip(dists, idxs):

        if i == j:
            continue

        if abs(i-j) < 500:
            continue

        if d < 5:

            best = (
                i, j, d
            )

            break

    if best:
        break

i1, i2, _ = best

if i1 > i2:
    i1, i2 = i2, i1

print()
print(
    f"Seam: {i1} {i2}"
)

wall_a = pts[
    i1:i2
]

wall_b = np.concatenate(
    (
        pts[i2:],
        pts[:i1]
    )
)

# reverse shorter side if needed

if len(wall_b) > len(wall_a):
    wall_b = wall_b[::-1]

plt.figure(
    figsize=(12,8)
)

plt.plot(
    wall_a[:,0],
    wall_a[:,1],
    linewidth=2,
    label="Wall A"
)

plt.plot(
    wall_b[:,0],
    wall_b[:,1],
    linewidth=2,
    label="Wall B"
)

plt.scatter(
    pts[i1,0],
    pts[i1,1],
    c="red",
    s=100,
    label="Seam A"
)

plt.scatter(
    pts[i2,0],
    pts[i2,1],
    c="green",
    s=100,
    label="Seam B"
)

plt.gca().set_aspect(
    "equal"
)

plt.legend()

plt.title(
    "Spielberg Graph-Based Wall Extraction"
)

plt.savefig(
    "experiments/spielberg_graph_walls.png",
    dpi=200,
    bbox_inches="tight"
)

print()
print(
    "Saved:"
    " experiments/spielberg_graph_walls.png"
)
