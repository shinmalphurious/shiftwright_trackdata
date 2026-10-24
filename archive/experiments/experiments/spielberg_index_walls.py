from pathlib import Path
from svgpathtools import svg2paths

import numpy as np
import matplotlib.pyplot as plt

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

    pts.append(
        [
            p.real,
            p.imag
        ]
    )

pts = np.array(
    pts
)

# Manually chosen from index map

split = 4000

wall_a = pts[:split]
wall_b = pts[split:]

wall_b = wall_b[::-1]

plt.figure(
    figsize=(14,10)
)

plt.plot(
    wall_a[:,0],
    wall_a[:,1],
    linewidth=3,
    label="Wall A"
)

plt.plot(
    wall_b[:,0],
    wall_b[:,1],
    linewidth=3,
    label="Wall B"
)

plt.gca().set_aspect(
    "equal"
)

plt.legend()

plt.title(
    "Index-Derived Wall Extraction"
)

plt.savefig(
    "experiments/spielberg_index_walls.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved:"
    " experiments/spielberg_index_walls.png"
)
