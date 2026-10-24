from pathlib import Path
from svgpathtools import svg2paths

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image, ImageDraw
from skimage.morphology import skeletonize
from scipy.spatial import KDTree

SVG = Path(
r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing\Road\spielberg\403-spielberg-gp\active.svg"
)

paths,_ = svg2paths(
    str(SVG)
)

path = paths[0]

N = 12000

polygon = []

for i in range(N):

    p = path.point(
        i/(N-1)
    )

    polygon.append(
        (
            p.real,
            p.imag
        )
    )

img = Image.new(
    "L",
    (1920,1080),
    0
)

draw = ImageDraw.Draw(
    img
)

draw.polygon(
    polygon,
    fill=255
)

binary = (
    np.array(img)
    > 0
)

skeleton = skeletonize(
    binary
)

ys,xs = np.where(
    skeleton
)

points = np.column_stack(
    (
        xs,
        ys
    )
)

tree = KDTree(
    points
)

remaining = set(
    range(len(points))
)

current = 0

ordered = [current]

remaining.remove(
    current
)

while remaining:

    dists, idxs = tree.query(
        points[current],
        k=20
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

ordered_pts = points[
    ordered
]

plt.figure(
    figsize=(14,8)
)

plt.plot(
    ordered_pts[:,0],
    ordered_pts[:,1],
    linewidth=2
)

plt.gca().invert_yaxis()

plt.gca().set_aspect(
    "equal"
)

plt.title(
    "Ordered Skeleton Path"
)

plt.savefig(
    "experiments/spielberg_ordered_skeleton.png",
    dpi=200,
    bbox_inches="tight"
)

np.savetxt(
    "experiments/spielberg_ordered_skeleton.csv",
    ordered_pts,
    delimiter=","
)

print()
print(
    "Saved:"
)

print(
    "experiments/spielberg_ordered_skeleton.png"
)

print(
    "experiments/spielberg_ordered_skeleton.csv"
)
