import json
from pathlib import Path
from svgpathtools import svg2paths

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

SVG = Path(
r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing\Road\spielberg\403-spielberg-gp\active.svg"
)

paths,_ = svg2paths(
    str(SVG)
)

path = paths[0]

N = 8000

pts = np.array([
[
path.point(i/(N-1)).real,
path.point(i/(N-1)).imag
]
for i in range(N)
])

split = 4052

outer = pts[:split]
inner = pts[split:]

tree = KDTree(inner)

centre = []

for p in outer:

    _, idx = tree.query(p)

    centre.append(
        (p + inner[idx]) / 2
    )

centre = np.array(
    centre
)

#
# nearest-neighbour chaining
#

remaining = set(
    range(len(centre))
)

current = 0

ordered = [current]

remaining.remove(
    current
)

centre_tree = KDTree(
    centre
)

while remaining:

    dists, idxs = centre_tree.query(
        centre[current],
        k=50
    )

    next_idx = None

    for idx in idxs:

        if idx in remaining:

            next_idx = idx
            break

    if next_idx is None:
        break

    ordered.append(
        next_idx
    )

    remaining.remove(
        next_idx
    )

    current = next_idx

ordered = centre[
    ordered
]

plt.figure(
    figsize=(12,8)
)

plt.plot(
    ordered[:,0],
    ordered[:,1],
    linewidth=3,
    color="black"
)

plt.gca().set_aspect(
    "equal"
)

plt.title(
    "Ordered KDTree Centreline"
)

plt.savefig(
    "experiments/spielberg_ordered_kdtree.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved: experiments/spielberg_ordered_kdtree.png"
)
