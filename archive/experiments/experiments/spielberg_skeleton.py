from pathlib import Path
from svgpathtools import svg2paths

import numpy as np

from PIL import Image
from PIL import ImageDraw

from skimage.morphology import skeletonize

SVG = Path(
r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing\Road\spielberg\403-spielberg-gp\active.svg"
)

paths, _ = svg2paths(str(SVG))

path = paths[0]

N = 12000

polygon = []

for i in range(N):

    p = path.point(i/(N-1))

    polygon.append(
        (
            float(p.real),
            float(p.imag)
        )
    )

img = Image.new(
    "L",
    (1920,1080),
    0
)

draw = ImageDraw.Draw(img)

draw.polygon(
    polygon,
    fill=255
)

binary = (
    np.array(img) > 0
)

skeleton = skeletonize(
    binary
)

np.save(
    "spielberg_skeleton.npy",
    skeleton
)

ys, xs = np.where(
    skeleton
)

points = np.column_stack(
    (
        xs,
        ys
    )
)

np.savetxt(
    "spielberg_skeleton_points.csv",
    points,
    delimiter=",",
    fmt="%d"
)

print()
print(
    f"Skeleton points: {len(points)}"
)

print()
print(
    "Saved:"
)

print(
    "spielberg_skeleton.npy"
)

print(
    "spielberg_skeleton_points.csv"
)
