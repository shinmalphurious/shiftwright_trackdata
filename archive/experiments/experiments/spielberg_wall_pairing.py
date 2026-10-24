from pathlib import Path
from svgpathtools import svg2paths

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

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

pts = np.array(pts)

split = 4052

outer = pts[:split]
inner = pts[split:]

tree = KDTree(
    inner
)

plt.figure(
    figsize=(14,10)
)

plt.plot(
    outer[:,0],
    outer[:,1],
    linewidth=1
)

plt.plot(
    inner[:,0],
    inner[:,1],
    linewidth=1
)

for i in range(
    0,
    len(outer),
    150
):

    dist, idx = tree.query(
        outer[i]
    )

    p1 = outer[i]
    p2 = inner[idx]

    plt.plot(
        [p1[0],p2[0]],
        [p1[1],p2[1]],
        linewidth=0.5,
        alpha=0.3
    )

plt.gca().set_aspect(
    "equal"
)

plt.title(
    "Wall Pairing Visualisation"
)

plt.savefig(
    "experiments/spielberg_wall_pairing.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved:"
    " experiments/spielberg_wall_pairing.png"
)
