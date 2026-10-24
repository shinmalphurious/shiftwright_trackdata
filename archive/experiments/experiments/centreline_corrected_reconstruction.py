import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

#
# Load telemetry
#

df = pd.read_csv(
    r"E:\track-knowledge\jacob_g61_vs_shiftwright.csv"
)

speed = df["SWSpeed"].values
yaw = np.radians(
    df["SWYaw"].values
)

#
# Load skeleton centreline
#

axis = np.loadtxt(
    r"E:\track-knowledge\generated\axes\403_axis.csv",
    delimiter=","
)

tree = KDTree(axis)

#
# Dead reckoning
#

dt = 1.0 / 60.0

x = [axis[0,0]]
y = [axis[0,1]]

correction_strength = 0.02

for i in range(
    1,
    len(speed)
):

    dx = (
        speed[i]
        * np.cos(yaw[i])
        * dt
    )

    dy = (
        speed[i]
        * np.sin(yaw[i])
        * dt
    )

    px = x[-1] + dx
    py = y[-1] + dy

    dist, idx = tree.query(
        [px,py]
    )

    cx, cy = axis[idx]

    px += (
        cx - px
    ) * correction_strength

    py += (
        cy - py
    ) * correction_strength

    x.append(px)
    y.append(py)

x = np.array(x)
y = np.array(y)

#
# draw
#

plt.figure(
    figsize=(14,8)
)

plt.plot(
    axis[:,0],
    axis[:,1],
    color="black",
    linewidth=3,
    label="Skeleton Axis"
)

plt.plot(
    x,
    y,
    color="red",
    linewidth=1,
    label="Centreline Corrected"
)

plt.gca().invert_yaxis()
plt.gca().set_aspect(
    "equal"
)

plt.legend()

plt.title(
    "Centreline Corrected Reconstruction"
)

plt.savefig(
    "centreline_corrected.png",
    dpi=250,
    bbox_inches="tight"
)

print(
    "Saved: centreline_corrected.png"
)
