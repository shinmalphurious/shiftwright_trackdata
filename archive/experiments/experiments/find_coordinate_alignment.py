import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv(
r"E:\track-knowledge\jacob_g61_vs_shiftwright.csv"
)

lat = df["Lat"].values
lon = df["Lon"].values

axis = np.loadtxt(
r"E:\track-knowledge\generated\axes\403_axis.csv",
delimiter=","
)

axis_x = axis[:,0]
axis_y = axis[:,1]

axis_x -= axis_x.min()
axis_y -= axis_y.min()

tests = [

("lat_lon", lat, lon),

("lon_lat", lon, lat),

("lon_neg_lat", lon, -lat),

("neg_lon_lat", -lon, lat),

("neg_lat_lon", -lat, lon),

("lat_neg_lon", lat, -lon)

]

for name, x, y in tests:

    x = x - x.min()
    y = y - y.min()

    x *= axis_x.max()/x.max()
    y *= axis_y.max()/y.max()

    plt.figure(
        figsize=(10,6)
    )

    plt.plot(
        axis_x,
        axis_y,
        color="black",
        linewidth=3
    )

    plt.plot(
        x,
        y,
        color="red"
    )

    plt.gca().invert_yaxis()
    plt.gca().set_aspect(
        "equal"
    )

    plt.title(name)

    plt.savefig(
        f"alignment_{name}.png",
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

print()
print(
    "Generated alignment comparisons"
)
