def merge_apexes(
    apexes,
    merge_distance=0.03
):

    if not apexes:
        return []

    apexes = sorted(
        apexes,
        key=lambda x:
        x["lap_pct"]
    )

    merged = [
        apexes[0]
    ]

    for apex in apexes[1:\]:

        previous = merged[-1]

        delta = (
            apex["lap_pct"]
            -
            previous["lap_pct"]
        )

        if delta < merge_distance:

            if (
                apex["curvature"]
                >
                previous["curvature"]
            ):
                merged[-1] = apex

        else:

            merged.append(
                apex
            )

    return merged
