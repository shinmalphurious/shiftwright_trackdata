from __future__ import annotations

def classify_context(
    following_straight_pct: float,
    next_gap_pct: float
) -> str:

    if next_gap_pct < 0.04:
        return "setup_corner"

    if following_straight_pct > 0.08:
        return "payoff_corner"

    return "isolated_corner"
