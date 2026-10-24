import numpy as np

from scipy.spatial import KDTree


def skeleton_to_points(
    skeleton
):

    ys, xs = np.where(
        skeleton
    )

    return np.column_stack(
        (
            xs,
            ys
        )
    )


def order_skeleton(
    points
):

    tree = KDTree(
        points
    )

    remaining = set(
        range(len(points))
    )

    start = np.argmin(
        points[:,0]
    )

    ordered = [start]

    remaining.remove(
        start
    )

    current = start

    while remaining:

        dists, idxs = tree.query(
            points[current],
            k=20
        )

        next_idx = None

        for idx in np.atleast_1d(idxs):

            if idx in remaining:

                next_idx = idx
                break

        if next_idx is None:
            break

        ordered.append(
            next_idx
        )

        remaining.remove(
            next_idx
        )

        current = next_idx

    return points[
        ordered
    ]
