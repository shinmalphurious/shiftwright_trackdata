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

    pts.append([
        p.real,
        p.imag
    ])

pts = np.array(pts)

vec = pts[1:] - pts[:-1]

angles = np.arctan2(
    vec[:,1],
    vec[:,0]
)

change = np.abs(
    np.unwrap(
        np.diff(
            angles
        )
    )
)

largest = np.argsort(
    change
)[-50:]

print()
print(
    "Largest direction changes"
)

for idx in largest[::-1]:

    print(
        idx,
        change[idx]
    )

plt.figure(
    figsize=(12,4)
)

plt.plot(
    change
)

plt.title(
    "Direction Change Profile"
)

plt.savefig(
    "experiments/spielberg_direction_change.png",
    dpi=200,
    bbox_inches="tight"
)

print()
print(
    "Saved:"
    " experiments/spielberg_direction_change.png"
)
