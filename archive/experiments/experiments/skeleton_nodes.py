from pathlib import Path
from PIL import Image
import numpy as np

from skimage.morphology import skeletonize
from scipy.signal import convolve2d

img = np.array(
    Image.open(
        "experiments/spielberg_skeleton.png"
    ).convert("L")
)

binary = img > 0

kernel = np.array(
[
[1,1,1],
[1,0,1],
[1,1,1]
]
)

degree = convolve2d(
    binary.astype(int),
    kernel,
    mode="same"
)

nodes = np.argwhere(
    binary &
    (degree != 2)
)

print()
print(
    f"Non-loop nodes: "
    f"{len(nodes)}"
)

for node in nodes[:50]:

    y,x = node

    print(
        f"x={x} y={y} "
        f"degree={degree[y,x]}"
    )
