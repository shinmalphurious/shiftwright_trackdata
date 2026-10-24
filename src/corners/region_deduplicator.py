from __future__ import annotations

def deduplicate_regions(
    corners,
    overlap_threshold=0.80
):

    if not corners:
        return []

    corners = sorted(
        corners,
        key=lambda c: c["strength"],
        reverse=True
    )

    kept = []

    for candidate in corners:

        c_start = candidate["start_pct"]
        c_end = candidate["end_pct"]

        keep = True

        for existing in kept:

            overlap_start = max(
                c_start,
                existing["start_pct"]
            )

            overlap_end = min(
                c_end,
                existing["end_pct"]
            )

            overlap = max(
                0.0,
                overlap_end - overlap_start
            )

            width = max(
                c_end - c_start,
                1e-6
            )

            overlap_ratio = (
                overlap / width
            )

            if overlap_ratio >= overlap_threshold:
                keep = False
                break

        if keep:
            kept.append(candidate)

    return sorted(
        kept,
        key=lambda c: c["apex_pct"]
    )
