from pathlib import Path
from svgpathtools import svg2paths
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

SVG = Path(
r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing\Road\spielberg\403-spielberg-gp\active.svg"
)

paths,_ = svg2paths(str(SVG))
path = paths[0]

N = 8000

pts = np.array([
[
path.point(i/(N-1)).real,
path.point(i/(N-1)).imag
]
for i in range(N)
])

split = 4052

wall_a = pts[:split]
wall_b = pts[split:][::-1]

def resample(curve,n=2000):

    seg = np.linalg.norm(
        curve[1:] - curve[:-1],
        axis=1
    )

    dist = np.concatenate(
        ([0], np.cumsum(seg))
    )

    target = np.linspace(
        0,
        dist[-1],
        n
    )

    fx = interp1d(
        dist,
        curve[:,0]
    )

    fy = interp1d(
        dist,
        curve[:,1]
    )

    return np.column_stack([
        fx(target),
        fy(target)
    ])

wall_a = resample(
    wall_a
)

wall_b = resample(
    wall_b
)

centre = (
    wall_a + wall_b
) / 2

plt.figure(
    figsize=(12,8)
)

plt.plot(
    wall_a[:,0],
    wall_a[:,1],
    alpha=0.5
)

plt.plot(
    wall_b[:,0],
    wall_b[:,1],
    alpha=0.5
)

plt.plot(
    centre[:,0],
    centre[:,1],
    color="black",
    linewidth=3
)

plt.gca().set_aspect(
    "equal"
)

plt.savefig(
    "experiments/spielberg_ordered_centreline.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved: experiments/spielberg_ordered_centreline.png"
)
