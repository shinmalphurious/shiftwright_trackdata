import numpy as np
from pathlib import Path
from svgpathtools import svg2paths
from scipy.interpolate import interp1d

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

pts = np.array(
    pts
)

split = 4053

outer = pts[:split]
inner = pts[split:]

def resample(curve,n=2000):

    seg = np.linalg.norm(
        curve[1:]-curve[:-1],
        axis=1
    )

    dist = np.concatenate(
        (
            [0],
            np.cumsum(seg)
        )
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

    return np.column_stack(
        (
            fx(target),
            fy(target)
        )
    )

outer = resample(
    outer
)

inner = resample(
    inner[::-1]
)

widths = np.linalg.norm(
    outer-inner,
    axis=1
)

print()
print(
    f"Mean   : {widths.mean():.3f}"
)

print(
    f"StdDev : {widths.std():.3f}"
)

print(
    f"Min    : {widths.min():.3f}"
)

print(
    f"Max    : {widths.max():.3f}"
)
