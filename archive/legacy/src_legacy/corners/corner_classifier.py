def classify_corner(
    strength,
    width_pct
):

    if strength > 0.020:

        return "hairpin"

    if strength > 0.010:

        return "medium"

    return "sweeper"
