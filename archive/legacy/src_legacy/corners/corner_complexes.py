from __future__ import annotations

def assign_complexes(
    corners,
    gap_threshold=0.04
):

    complexes = []

    current = []

    for i, corner in enumerate(corners):

        if not current:
            current = [i + 1]
            continue

        previous = corners[i - 1]

        gap = (
            corner["start_pct"]
            -
            previous["end_pct"]
        )

        if gap < 0:
            gap += 1.0

        if gap <= gap_threshold:

            current.append(
                i + 1
            )

        else:

            complexes.append(
                current
            )

            current = [
                i + 1
            ]

    if current:
        complexes.append(
            current
        )

    return complexes
