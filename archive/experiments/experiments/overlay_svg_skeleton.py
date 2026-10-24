import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from svgpathtools import svg2paths

SVG = Path(
r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing\Road\spielberg\403-spielberg-gp\active.svg"
)

paths,_ = svg2paths(
    str(SVG)
)

path = paths[0]

#
# SVG ribbon
#

N = 12000

ribbon = np.array([
[
    path.point(i/(N-1)).real,
    path.point(i/(N-1)).imag
]
for i in range(N)
])

#
# Skeleton centreline
#

skeleton = np.load(
    "spielberg_skeleton.npy"
)

ys, xs = np.where(
    skeleton
)

#
# Plot
#

plt.figure(
    figsize=(14,8)
)

plt.plot(
    ribbon[:,0],
    ribbon[:,1],
    color="green",
    linewidth=1,
    alpha=0.7,
    label="SVG Ribbon"
)

plt.scatter(
    xs,
    ys,
    s=1,
    color="red",
    label="Skeleton"
)

plt.gca().invert_yaxis()

plt.gca().set_aspect(
    "equal"
)

plt.legend()

plt.title(
    "SVG Ribbon vs Skeleton Centreline"
)

plt.savefig(
    "svg_vs_skeleton.png",
    dpi=250,
    bbox_inches="tight"
)

print()
print(
    "Saved:"
)

print(
    "svg_vs_skeleton.png"
)
