import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv(
    r"E:\track-knowledge\jacob_g61_vs_shiftwright.csv"
)

speed = df[
    "SWSpeed"
].values

yaw = np.radians(
    df["SWYaw"].values
)

#
# assume 60hz initially
#

dt = 1.0 / 60.0

x = [0.0]
y = [0.0]

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

    x.append(
        x[-1] + dx
    )

    y.append(
        y[-1] + dy
    )

x = np.array(x)
y = np.array(y)

plt.figure(
    figsize=(12,8)
)

plt.plot(
    x,
    y,
    linewidth=2
)

plt.gca().set_aspect(
    "equal"
)

plt.title(
    "Shiftwright Raw Reconstruction"
)

plt.savefig(
    "raw_dead_reckoning.png",
    dpi=200,
    bbox_inches="tight"
)

print(
    "Saved:"
    " raw_dead_reckoning.png"
)
