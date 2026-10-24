import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

#
# Shiftwright reconstruction
#

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

#
# Skeleton axis
#

axis = np.loadtxt(
    r"E:\track-knowledge\generated\axes\403_axis.csv",
    delimiter=","
)

axis_x = axis[:,0].copy()
axis_y = axis[:,1].copy()

#
# Normalize
#

x -= x.min()
y -= y.min()

axis_x -= axis_x.min()
axis_y -= axis_y.min()

#
# Scale search
#

tree = KDTree(
    np.column_stack(
        (
            axis_x,
            axis_y
        )
    )
)

best_scale = None
best_error = float("inf")

for scale in np.linspace(
    0.70,
    1.30,
    121
):

    sx = x * scale
    sy = y * scale

    total_error = 0.0

    for px, py in zip(
        sx[::10],
        sy[::10]
    ):

        dist, _ = tree.query(
            [px, py]
        )

        total_error += dist

    if total_error < best_error:

        best_error = total_error
        best_scale = scale

print()
print(
    f"Best Scale: {best_scale:.4f}"
)

print(
    f"Error: {best_error:.2f}"
)

#
# Final plot
#

sx = x * best_scale
sy = y * best_scale

plt.figure(
    figsize=(14,8)
)

plt.plot(
    axis_x,
    axis_y,
    color="black",
    linewidth=3,
    label="Skeleton Axis"
)

plt.plot(
    sx,
    sy,
    color="red",
    linewidth=1,
    label=f"Scaled Reconstruction ({best_scale:.3f})"
)

plt.gca().invert_yaxis()
plt.gca().set_aspect(
    "equal"
)

plt.legend()

plt.title(
    "Scale Fit Validation"
)

plt.savefig(
    "scale_fit_validation.png",
    dpi=250,
    bbox_inches="tight"
)

print()
print(
    "Saved: scale_fit_validation.png"
)
