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

pts = np.array(
    pts
)

plt.figure(
    figsize=(14,10)
)

scatter = plt.scatter(
    pts[:,0],
    pts[:,1],
    c=np.arange(N),
    s=2,
    cmap="turbo"
)

plt.colorbar(
    scatter,
    label="Path Index"
)

plt.gca().set_aspect(
    "equal"
)

plt.title(
    "Spielberg Perimeter Index Mapping"
)

plt.savefig(
    "experiments/spielberg_index_map.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved: experiments/spielberg_index_map.png"
)
