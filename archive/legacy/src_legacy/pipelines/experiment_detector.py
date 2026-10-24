from __future__ import annotations

import json
import numpy as np
from pathlib import Path

from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

ROOT = Path(__file__).resolve().parents[2]

AXIS = ROOT / "generated" / "axes_normalized"

TRACKS = [219,324,403]


def count_corners(
    axis_points,
    percentile,
    prominence_scale,
    distance
):

    x = gaussian_filter1d(
        axis_points[:,1],
        sigma=5
    )

    y = gaussian_filter1d(
        axis_points[:,2],
        sigma=5
    )

    dx = np.gradient(x)
    dy = np.gradient(y)

    ddx = np.gradient(dx)
    ddy = np.gradient(dy)

    curvature = np.abs(
        dx * ddy -
        dy * ddx
    )

    denom = np.power(
        dx*dx + dy*dy,
        1.5
    )

    curvature = np.divide(
        curvature,
        denom,
        out=np.zeros_like(curvature),
        where=denom>0
    )

    curvature = gaussian_filter1d(
        curvature,
        sigma=10
    )

    threshold = (
        np.percentile(
            curvature,
            percentile
        )
    )

    peaks, _ = find_peaks(
        curvature,
        prominence=
            threshold *
            prominence_scale,
        distance=distance
    )

    return len(peaks)


for percentile in [90,92,95]:

    for prominence in [0.25,0.35,0.50]:

        for distance in [40,60,80]:

            print()

            print(
                percentile,
                prominence,
                distance
            )

            for track in TRACKS:

                data = np.loadtxt(
                    AXIS /
                    f"{track}_axis.csv",
                    delimiter=",",
                    skiprows=1
                )

                count = count_corners(
                    data,
                    percentile,
                    prominence,
                    distance
                )

                print(
                    track,
                    count
                )
