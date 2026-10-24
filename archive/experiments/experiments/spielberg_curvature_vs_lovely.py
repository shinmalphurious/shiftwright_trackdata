from pathlib import Path
from svgpathtools import svg2paths

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from scipy.ndimage import gaussian_filter1d

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

    _, idx = tree.query(p)

    q = inner[idx]

    centre.append(
        (p + q) / 2
    )

centre = np.array(
    centre
)

x = gaussian_filter1d(
    centre[:,0],
    sigma=5
)

y = gaussian_filter1d(
    centre[:,1],
    sigma=5
)

dx = np.gradient(x)
dy = np.gradient(y)

ddx = np.gradient(dx)
ddy = np.gradient(dy)

curvature = np.abs(
    dx * ddy
    -
    dy * ddx
)

denom = np.power(
    dx*dx + dy*dy,
    1.5
)

curvature = np.divide(
    curvature,
    denom,
    out=np.zeros_like(curvature),
    where=denom>0
)

curvature = gaussian_filter1d(
    curvature,
    sigma=10
)

lap = np.linspace(
    0,
    1,
    len(curvature)
)

plt.figure(
    figsize=(14,5)
)

plt.plot(
    lap,
    curvature,
    linewidth=2
)

for marker in [
    0.075,
    0.29,
    0.47,
    0.59,
    0.675,
    0.83,
    0.905
]:

    plt.axvline(
        marker,
        linestyle="--",
        alpha=0.3
    )

plt.title(
    "Spielberg Smoothed Curvature vs Lovely Corner Locations"
)

plt.xlabel(
    "Lap Percentage"
)

plt.ylabel(
    "Curvature"
)

plt.savefig(
    "experiments/spielberg_curvature_vs_lovely.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved: experiments/spielberg_curvature_vs_lovely.png"
)
