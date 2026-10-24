from pathlib import Path
import numpy as np

AXIS_DIR = Path(
    "generated/axes"
)

OUTPUT_DIR = Path(
    "generated/axes_normalized"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

TARGET_POINTS = 2048

built = 0

for axis_file in AXIS_DIR.glob(
    "*_axis.csv"
):

    try:

        pts = np.loadtxt(
            axis_file,
            delimiter=","
        )

        if len(pts) < 10:
            continue

        seg = np.linalg.norm(
            pts[1:] - pts[:-1],
            axis=1
        )

        cumulative = np.concatenate(
            (
                [0],
                np.cumsum(seg)
            )
        )

        target_dist = np.linspace(
            0,
            cumulative[-1],
            TARGET_POINTS
        )

        x = np.interp(
            target_dist,
            cumulative,
            pts[:,0]
        )

        y = np.interp(
            target_dist,
            cumulative,
            pts[:,1]
        )

        lap_pct = np.linspace(
            0.0,
            1.0,
            TARGET_POINTS
        )

        normalized = np.column_stack(
            (
                lap_pct,
                x,
                y
            )
        )

        np.savetxt(
            OUTPUT_DIR / axis_file.name,
            normalized,
            delimiter=",",
            fmt=[
                "%.6f",
                "%.3f",
                "%.3f"
            ],
            header="lap_pct,x,y",
            comments=""
        )

        built += 1

    except Exception as ex:

        print(
            f"FAIL {axis_file.name}: "
            f"{ex}"
        )

print()
print(
    f"Normalized: {built}"
)
