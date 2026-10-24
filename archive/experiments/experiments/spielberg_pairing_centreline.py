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

tree = KDTree(inner)

centre = []

for p in outer:

    dist, idx = tree.query(p)

    q = inner[idx]

    centre.append(
        (p + q) / 2
    )

centre = np.array(
    centre
)

plt.figure(
    figsize=(14,10)
)

plt.plot(
    outer[:,0],
    outer[:,1],
    linewidth=1,
    alpha=0.5
)

plt.plot(
    inner[:,0],
    inner[:,1],
    linewidth=1,
    alpha=0.5
)

plt.plot(
    centre[:,0],
    centre[:,1],
    linewidth=3,
    color="black",
    label="Centreline"
)

plt.gca().set_aspect(
    "equal"
)

plt.legend()

plt.title(
    "Nearest Wall Centreline"
)

plt.savefig(
    "experiments/spielberg_pairing_centreline.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved:"
    " experiments/spielberg_pairing_centreline.png"
)
