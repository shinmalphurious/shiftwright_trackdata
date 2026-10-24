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

pts = np.array(pts)

split = 4053

a = pts[:split]
b = pts[split:]

tree = KDTree(b)

widths = []

for point in a:

    distance, _ = tree.query(
        point
    )

    widths.append(
        distance
    )

widths = np.array(
    widths
)

print()
print(
    f"Mean Width : "
    f"{widths.mean():.2f}"
)

print(
    f"Min Width  : "
    f"{widths.min():.2f}"
)

print(
    f"Max Width  : "
    f"{widths.max():.2f}"
)

smallest = np.argsort(
    widths
)[:20]

largest = np.argsort(
    widths
)[-20:]

print()
print("Smallest Widths")

for idx in smallest:

    print(
        idx,
        widths[idx]
    )

print()
print("Largest Widths")

for idx in largest:

    print(
        idx,
        widths[idx]
    )

plt.figure(
    figsize=(12,5)
)

plt.plot(
    widths
)

plt.title(
    "Spielberg Width Profile"
)

plt.savefig(
    "experiments/spielberg_width_profile.png",
    dpi=200,
    bbox_inches="tight"
)

print()
print(
    "Saved:"
    " experiments/spielberg_width_profile.png"
)
