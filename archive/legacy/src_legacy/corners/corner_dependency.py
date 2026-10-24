from __future__ import annotations

def calculate_exit_importance(
    following_straight_pct: float
) -> float:

    score = min(
        following_straight_pct / 0.15,
        1.0
    )

    return round(score, 4)
