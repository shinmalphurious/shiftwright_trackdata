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

tree = KDTree(
    pts
)

pairs = []

for i in range(N):

    dists, idxs = tree.query(
        pts[i],
        k=20
    )

    for d, j in zip(dists, idxs):

        if i == j:
            continue

        if abs(i - j) < 500:
            continue

        if d < 5:

            pairs.append(
                (
                    i,
                    j,
                    d
                )
            )

pairs.sort(
    key=lambda x: x[2]
)

print()
print(
    "Best seam candidates:"
)

for pair in pairs[:20]:


    print(pair)

i1, i2, _ = pairs[0]

print()
print(
    f"Using seam pair:"
    f" {i1} {i2}"
)

if i1 > i2:
    i1, i2 = i2, i1

boundary_a = pts[
    i1:i2
]

boundary_b = np.concatenate(
    (
        pts[i2:],
        pts[:i1]
    )
)

plt.figure(
    figsize=(12,8)
)

plt.plot(
    boundary_a[:,0],
    boundary_a[:,1],
    label="Boundary A"
)

plt.plot(
    boundary_b[:,0],
    boundary_b[:,1],
    label="Boundary B"
)

plt.gca().set_aspect(
    "equal"
)

plt.title(
    "Spielberg Two Wall Extraction"
)

plt.legend()

plt.savefig(
    "experiments/spielberg_two_walls.png",
    dpi=200,
    bbox_inches="tight"
)

print()
print(
    "Saved:"
    " experiments/spielberg_two_walls.png"
)
