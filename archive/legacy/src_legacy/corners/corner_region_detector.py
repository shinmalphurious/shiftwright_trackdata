import numpy as np


def expand_corner_region(
    curvature,
    apex_idx,
    threshold_ratio=0.35,
    max_width_pct=0.15
):

    peak = curvature[
        apex_idx
    ]

    threshold = (
        peak *
        threshold_ratio
    )

    max_span = int(
        len(curvature) *
        max_width_pct
    )

    start = apex_idx

    while (
        start > 0
        and
        curvature[start] > threshold
        and
        (apex_idx - start) < max_span
    ):
        start -= 1

    end = apex_idx

    while (
        end < len(curvature)-1
        and
        curvature[end] > threshold
        and
        (end - apex_idx) < max_span
    ):
        end += 1

    return (
        start,
        apex_idx,
        end
    )
