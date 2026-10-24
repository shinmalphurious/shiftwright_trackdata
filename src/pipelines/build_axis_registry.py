from pathlib import Path
import numpy as np
import json

AXIS_DIR = Path(
    "generated/axes_normalized"
)

OUTPUT = Path(
    "generated/axis_registry.json"
)

registry = {}

for axis in AXIS_DIR.glob(
    "*_axis.csv"
):

    track_id = (
        axis.stem
        .replace(
            "_axis",
            ""
        )
    )

    pts = np.loadtxt(
        axis,
        delimiter=",",
        skiprows=1
    )

    registry[track_id] = {

        "track_id":
            int(track_id),

        "axis_points":
            int(len(pts)),

        "lap_coordinate_system":
            "lap_pct",

        "start_pct":
            0.0,

        "end_pct":
            1.0
    }

with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        dict(
            sorted(
                registry.items(),
                key=lambda x: int(x[0])
            )
        ),
        fp,
        indent=2
    )

print()
print(
    f"Registered: {len(registry)}"
)
