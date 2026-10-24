import numpy as np

def corner_angle(
    axis,
    start_idx,
    end_idx
):

    p1 = axis[start_idx][1:3]

    p2 = axis[end_idx][1:3]

    vec = p2 - p1

    return np.degrees(
        np.arctan2(
            vec[1],
            vec[0]
        )
    )


def corner_width_pct(
    start_pct,
    end_pct
):

    return (
        end_pct
        -
        start_pct
    )
