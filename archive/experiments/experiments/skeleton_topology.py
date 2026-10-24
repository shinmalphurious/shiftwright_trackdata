import numpy as np
from scipy.signal import convolve2d

skeleton = np.load(
    "spielberg_skeleton.npy"
)

kernel = np.array(
[
[1,1,1],
[1,0,1],
[1,1,1]
]
)

neighbors = convolve2d(
    skeleton.astype(int),
    kernel,
    mode="same"
)

endpoints = (
    skeleton &
    (neighbors == 1)
)

junctions = (
    skeleton &
    (neighbors > 2)
)

print()

print(
    f"Skeleton Pixels: "
    f"{int(skeleton.sum())}"
)

print(
    f"Endpoints: "
    f"{int(endpoints.sum())}"
)

print(
    f"Junctions: "
    f"{int(junctions.sum())}"
)
