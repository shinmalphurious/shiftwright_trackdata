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

    pts.append([
        p.real,
        p.imag
    ])

pts = np.array(pts)

split_index = 4053
trim = 20

boundary_a = pts[:split_index]
boundary_b = pts[split_index:]

boundary_a = boundary_a[
    trim:-trim
]

boundary_b = boundary_b[
    trim:-trim
]

boundary_b = boundary_b[::-1]

def resample_curve(curve, n=2000):

    seg = np.linalg.norm(
        curve[1:] - curve[:-1],
        axis=1
    )

    cumulative = np.concatenate(
        (
            [0],
            np.cumsum(seg)
        )
    )

    target = np.linspace(
        0,
        cumulative[-1],
        n
    )

    x = np.interp(
        target,
        cumulative,
        curve[:,0]
    )

    y = np.interp(
        target,
        cumulative,
        curve[:,1]
    )

    return np.column_stack(
        [x,y]
    )

outer = resample_curve(
    boundary_a
)

inner = resample_curve(
    boundary_b
)

centre = (
    outer + inner
) / 2

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
    color="black",
    label="Centreline"
)

plt.gca().set_aspect(
    "equal"
)

plt.legend()

plt.title(
    "Spielberg Arc Length Centreline"
)

plt.savefig(
    "experiments/spielberg_arc_length_centreline.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved: experiments/spielberg_arc_length_centreline.png"
)
