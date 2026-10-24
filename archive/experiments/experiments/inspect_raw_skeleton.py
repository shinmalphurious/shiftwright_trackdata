import numpy as np
import matplotlib.pyplot as plt

skeleton = np.load(
    "experiments/spielberg_skeleton.npy"
)

ys, xs = np.where(
    skeleton
)

points = np.column_stack(
    (
        xs,
        ys
    )
)

print()
print(
    f"Actual skeleton points: "
    f"{len(points)}"
)

plt.figure(
    figsize=(12,8)
)

plt.scatter(
    xs,
    ys,
    s=1
)

plt.gca().invert_yaxis()
plt.gca().set_aspect(
    "equal"
)

plt.title(
    "Raw Skeleton Points"
)

plt.savefig(
    "experiments/raw_skeleton_points.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved:"
    " experiments/raw_skeleton_points.png"
)
