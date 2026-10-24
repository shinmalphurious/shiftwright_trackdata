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

        if abs(i-j) < 500:
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
    key=lambda x:x[2]
)

plt.figure(
    figsize=(14,10)
)

plt.plot(
    pts[:,0],
    pts[:,1],
    linewidth=1
)

for idx,(i,j,d) in enumerate(
    pairs[:20]
):

    plt.scatter(
        pts[i,0],
        pts[i,1],
        s=60,
        label=f"A{idx}"
    )

    plt.scatter(
        pts[j,0],
        pts[j,1],
        s=60,
        label=f"B{idx}"
    )

plt.gca().set_aspect(
    "equal"
)

plt.title(
    "Potential Ribbon Seam Locations"
)

plt.savefig(
    "experiments/spielberg_seam_debug.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved:"
    " experiments/spielberg_seam_debug.png"
)
