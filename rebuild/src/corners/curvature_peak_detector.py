import numpy as np

from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks


def detect_corner_candidates(
    axis_points
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
        dx * ddy
        -
        dy * ddx
    )

    denom = np.power(
        dx * dx + dy * dy,
        1.5
    )

    curvature = np.divide(
        curvature,
        denom,
        out=np.zeros_like(curvature),
        where=denom > 0
    )

    curvature = gaussian_filter1d(
        curvature,
        sigma=10
    )

    threshold = (
        np.percentile(
            curvature,
            90
        ) * 0.25
    )

    peaks, _ = find_peaks(
        curvature,
        prominence=threshold,
        distance=40
    )

    return peaks, curvature
