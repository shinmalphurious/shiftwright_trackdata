import pandas as pd
import numpy as np
from scipy.spatial import KDTree

df = pd.read_csv(
    r"E:\track-knowledge\jacob_g61_vs_shiftwright.csv"
)

x = np.array(
    df["Lon"],
    dtype=float
)

y = -np.array(
    df["Lat"],
    dtype=float
)

axis = np.loadtxt(
    r"E:\track-knowledge\generated\axes\403_axis.csv",
    delimiter=","
)

#
# use proven transform
#

x -= x.min()
y -= y.min()

axis_x = axis[:,0]
axis_y = axis[:,1]

axis_x -= axis_x.min()
axis_y -= axis_y.min()

#
# scale using dimensions
#

sx = (
    axis_x.max()
    /
    x.max()
)

sy = (
    axis_y.max()
    /
    y.max()
)

x *= sx
y *= sy

tree = KDTree(
    np.column_stack(
        (
            axis_x,
            axis_y
        )
    )
)

distances = []

for px, py in zip(
    x,
    y
):

    dist, _ = tree.query(
        [px,py]
    )

    distances.append(
        dist
    )

distances = np.array(
    distances
)

print()

print(
    f"Mean Offset: "
    f"{distances.mean():.2f}"
)

print(
    f"Median Offset: "
    f"{np.median(distances):.2f}"
)

print(
    f"95th Percentile: "
    f"{np.percentile(distances,95):.2f}"
)

print(
    f"Max Offset: "
    f"{distances.max():.2f}"
)
