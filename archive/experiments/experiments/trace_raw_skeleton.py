import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

skeleton = np.load(
    "spielberg_skeleton.npy"
)

ys, xs = np.where(
    skeleton
)

pts = np.column_stack(
    (
        xs,
        ys
    )
)

tree = KDTree(
    pts
)

remaining = set(
    range(len(pts))
)

start = np.argmin(
    xs
)

ordered = [start]

remaining.remove(
    start
)

current = start

while remaining:

    dists, idxs = tree.query(
        pts[current],
        k=20
    )

    next_idx = None

    for idx in np.atleast_1d(idxs):

        if idx in remaining:

            next_idx = idx
            break

    if next_idx is None:
        break

    ordered.append(
        next_idx
    )

    remaining.remove(
        next_idx
    )

    current = next_idx

ordered_pts = pts[
    ordered
]

plt.figure(
    figsize=(12,8)
)

plt.plot(
    ordered_pts[:,0],
    ordered_pts[:,1],
    linewidth=2
)

plt.gca().invert_yaxis()
plt.gca().set_aspect(
    "equal"
)

plt.title(
    "Ordered Raw Skeleton Loop"
)

plt.savefig(
    "ordered_raw_skeleton.png",
    dpi=200,
    bbox_inches="tight"
)

np.savetxt(
    "ordered_raw_skeleton.csv",
    ordered_pts,
    delimiter=",",
    fmt="%d"
)

print()
print(
    f"Ordered points: "
    f"{len(ordered_pts)}"
)

print(
    "Saved:"
)

print(
    "ordered_raw_skeleton.png"
)

print(
    "ordered_raw_skeleton.csv"
)
