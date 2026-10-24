from pathlib import Path

import matplotlib.pyplot as plt

from svgpathtools import svg2paths


SVG_FILE = Path(
r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing\Road\spielberg\403-spielberg-gp\active.svg"
)

paths, _ = svg2paths(
    str(SVG_FILE)
)

print()
print(
    f"Paths: {len(paths)}"
)

path = paths[0]

samples = []

for i in range(5000):

    t = i / 4999

    point = path.point(t)

    samples.append(
        (
            point.real,
            point.imag
        )
    )

xs = [
    p[0]
    for p in samples
]

ys = [
    p[1]
    for p in samples
]

plt.figure(
    figsize=(10,6)
)

plt.plot(
    xs,
    ys,
    linewidth=1
)

plt.gca().set_aspect(
    "equal"
)

plt.title(
    "Spielberg Active SVG Sampled Path"
)

plt.savefig(
    "experiments/spielberg_path.png",
    dpi=200,
    bbox_inches="tight"
)

print()
print(
    "Saved: experiments/spielberg_path.png"
)
