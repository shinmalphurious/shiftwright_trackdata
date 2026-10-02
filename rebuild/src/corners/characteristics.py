from __future__ import annotations


def classify_corner(angle_deg: float) -> str:
    if angle_deg < 20:
        return "kink"

    if angle_deg < 60:
        return "bend"

    if angle_deg < 120:
        return "corner"

    return "hairpin"


def calculate_severity(
    angle_deg: float,
    strength: float
) -> float:

    angle_component = min(
        max(angle_deg / 180.0, 0.0),
        1.0
    )

    strength_component = min(
        max(strength / 0.03, 0.0),
        1.0
    )

    return round(
        0.6 * angle_component +
        0.4 * strength_component,
        4
    )
