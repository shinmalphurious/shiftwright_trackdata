from pathlib import Path
from svgpathtools import svg2paths

import numpy as np
import matplotlib.pyplot as plt

SVG_FILE = Path(
r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing\Road\spielberg\403-spielberg-gp\active.svg"
)

paths, _ = svg2paths(
    str(SVG_FILE)
)

path = paths[0]

N = 4000

pts = []

for i in range(N):

    t = i / (N - 1)

    p = path.point(t)

    pts.append(
        [
            p.real,
            p.imag
        ]
    )

pts = np.array(pts)

half = len(pts) // 2

outer = pts[:half]

inner = pts[half:]

inner = inner[::-1]

count = min(
    len(outer),
    len(inner)
)

outer = outer[:count]
inner = inner[:count]

centre = (
    outer + inner
) / 2.0

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

plt.plot(
    centre[:,0],
    centre[:,1],
    linewidth=2,
    label="Centreline"
)

plt.gca().set_aspect(
    "equal"
)

plt.legend()

plt.title(
    "Spielberg Centreline Reconstruction"
)

plt.savefig(
    "experiments/spielberg_centreline.png",
    dpi=200,
    bbox_inches="tight"
)

print()
print(
    "Saved: experiments/spielberg_centreline.png"
)
