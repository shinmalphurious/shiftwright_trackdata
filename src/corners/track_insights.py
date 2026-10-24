from __future__ import annotations

def classify_insight(
    severity: float,
    exit_importance: float
) -> list[str\]:

    tags = []

    if exit_importance >= 0.8:
        tags.append(
            "critical_exit"
        )

    if severity >= 0.7:
        tags.append(
            "heavy_braking_candidate"
        )

    return tags
