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

split_index = 4053

boundary_a = pts[
    :split_index
]

boundary_b = pts[
    split_index:
]

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

plt.legend()

plt.title(
    "Spielberg Boundary Split"
)

plt.savefig(
    "experiments/spielberg_boundary_split.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved:"
    " experiments/spielberg_boundary_split.png"
)
