import re
from pathlib import Path
from svgpathtools import svg2paths

import numpy as np
from scipy.spatial import KDTree

TRACK_ID = 403

AXIS_FILE = Path(
    f"generated/axes_normalized/{TRACK_ID}_axis.csv"
)

START_FINISH_SVG = Path(
r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing\Road\spielberg\403-spielberg-gp\start-finish.svg"
)

#
# LOAD AXIS
#

axis = np.loadtxt(
    AXIS_FILE,
    delimiter=",",
    skiprows=1
)

#
# PARSE START/FINISH SVG
#

text = START_FINISH_SVG.read_text(
    encoding="utf-8",
    errors="ignore"
)

coords = re.findall(
    r'([0-9]+(?:\.[0-9]+)?),([0-9]+(?:\.[0-9]+)?)',
    text
)

pts = np.array(
    [
        [
            float(x),
            float(y)
        ]
        for x,y
        in coords
    ]
)

start_finish = pts.mean(
    axis=0
)

#
# FIND NEAREST AXIS POINT
#

tree = KDTree(
    axis[:,1:3]
)

_, idx = tree.query(
    start_finish
)

print()
print(
    f"Start/Finish Axis Index: "
    f"{idx}"
)

print(
    f"LapPct Before: "
    f"{axis[idx][0]:.6f}"
)

#
# ROTATE AXIS
#

rotated = np.vstack(
    (
        axis[idx:],
        axis[:idx]
    )
)

lap_pct = np.linspace(
    0.0,
    1.0,
    len(rotated)
)

rotated[:,0] = lap_pct

np.savetxt(
    f"generated/axes_normalized/{TRACK_ID}_axis_aligned.csv",
    rotated,
    delimiter=",",
    fmt=[
        "%.6f",
        "%.3f",
        "%.3f"
    ],
    header="lap_pct,x,y",
    comments=""
)

print()
print(
    f"Saved:"
)

print(
    f"generated/axes_normalized/{TRACK_ID}_axis_aligned.csv"
)
