from pathlib import Path
import numpy as np
from PIL import Image

img = np.array(
    Image.open(
        "experiments/spielberg_skeleton.png"
    ).convert("L")
)

binary = img > 0

ys,xs = np.where(binary)

print()
print(
    f"Skeleton pixels: {len(xs)}"
)

print(
    f"Bounds X: {xs.min()}-{xs.max()}"
)

print(
    f"Bounds Y: {ys.min()}-{ys.max()}"
)

# Export actual skeleton points

pts = np.column_stack(
    (xs,ys)
)

np.savetxt(
    "experiments/spielberg_skeleton_points.csv",
    pts,
    delimiter=",",
    fmt="%d"
)

print()
print(
    "Saved:"
)

print(
    "experiments/spielberg_skeleton_points.csv"
)
