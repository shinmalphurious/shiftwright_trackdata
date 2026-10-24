import numpy as np

from scipy.ndimage import gaussian_filter1d


def curvature_profile(
    points
):

    x = gaussian_filter1d(
        points[:,0],
        sigma=5
    )

    y = gaussian_filter1d(
        points[:,1],
        sigma=5
    )

    dx = np.gradient(x)
    dy = np.gradient(y)

    ddx = np.gradient(dx)
    ddy = np.gradient(dy)

    num = np.abs(
        dx * ddy
        -
        dy * ddx
    )

    den = np.power(
        dx*dx + dy*dy,
        1.5
    )

    return np.divide(
        num,
        den,
        out=np.zeros_like(num),
        where=den>0
    )
