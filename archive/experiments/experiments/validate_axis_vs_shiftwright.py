import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#
# Reconstructed trajectory
#

df = pd.read_csv(
    r"E:\track-knowledge\jacob_g61_vs_shiftwright.csv"
)

lap = df[
    "LapDistPct"
].values

lat = df[
    "Lat"
].values

lon = df[
    "Lon"
].values

#
# Skeleton Axis
#

axis = np.loadtxt(
    r"E:\track-knowledge\generated\axes\403_axis.csv",
    delimiter=","
)

#
# Normalize both
#

lat = lat - lat.min()
lon = lon - lon.min()

axis_x = axis[:,0]
axis_y = axis[:,1]

axis_x = (
    axis_x - axis_x.min()
)

axis_y = (
    axis_y - axis_y.min()
)

#
# Scale to same range
#

lat *= axis_x.max() / lat.max()
lon *= axis_y.max() / lon.max()

#
# Draw
#

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
    lat,
    lon,
    color="red",
    linewidth=1,
    label="Shiftwright Reconstruction"
)

plt.gca().invert_yaxis()

plt.gca().set_aspect(
    "equal"
)

plt.legend()

plt.title(
    "Skeleton Axis vs Shiftwright Reconstruction"
)

plt.savefig(
    "axis_vs_shiftwright.png",
    dpi=250,
    bbox_inches="tight"
)

print(
    "Saved: axis_vs_shiftwright.png"
)
