import json
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

# confirmed seam pair

i1 = 4053
i2 = 0

wall_a = pts[
    :i1
]

wall_b = pts[
    i1:
]

# explicitly close loops

wall_a = np.vstack(
    [
        wall_a,
        wall_a[0]
    ]
)

wall_b = np.vstack(
    [
        wall_b,
        wall_b[0]
    ]
)

# determine area

def signed_area(curve):

    x = curve[:,0]
    y = curve[:,1]

    return 0.5 * np.sum(
        x[:-1]*y[1:]
        -
        x[1:]*y[:-1]
    )

area_a = abs(
    signed_area(
        wall_a
    )
)

area_b = abs(
    signed_area(
        wall_b
    )
)

if area_a > area_b:

    outer = wall_a
    inner = wall_b

else:

    outer = wall_b
    inner = wall_a

plt.figure(
    figsize=(12,8)
)

plt.plot(
    outer[:,0],
    outer[:,1],
    linewidth=3,
    label="Outer Wall"
)

plt.plot(
    inner[:,0],
    inner[:,1],
    linewidth=3,
    label="Inner Wall"
)

plt.gca().set_aspect(
    "equal"
)

plt.legend()

plt.title(
    "Closed Wall Extraction"
)

plt.savefig(
    "experiments/spielberg_closed_walls.png",
    dpi=200,
    bbox_inches="tight"
)

print()
print(
    f"Outer Area: {area_a:.1f}"
)

print(
    f"Inner Area: {area_b:.1f}"
)

print()
print(
    "Saved:"
    " experiments/spielberg_closed_walls.png"
)
