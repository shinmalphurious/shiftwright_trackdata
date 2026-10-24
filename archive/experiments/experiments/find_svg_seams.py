from pathlib import Path
from svgpathtools import svg2paths
import numpy as np

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

distances = np.linalg.norm(
    pts[1:] - pts[:-1],
    axis=1
)

largest = np.argsort(
    distances
)[-10:]

print()
print("Largest Perimeter Jumps")

for idx in largest:

    print(
        f"Index={idx} "
        f"Distance={distances[idx]:.3f}"
    )
