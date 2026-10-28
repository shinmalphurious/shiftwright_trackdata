"""The claims research may propose about a corner, and how evidence tests them.

Research (a model or geometry rules) may only propose claims from CLAIMS. Each claim has
deterministic tests, so validation never depends on a model:
    transcript(note)  -> "confirm", "contradict" or None, on what a speaker said about the corner;
                         note is {field: text} with braking, gear, line, exit, mistakes, spoken_as
    telemetry(metrics)-> "confirm", "contradict" or None, on src.shared.telemetry_landmarks.corner_metrics
    approach_dependent: whether the claim depends on the corners around it (a chicane variant
                        changes the braking into the next corner), which limits inheritance.
    coach_field:        the Shiftwright corner field a validated claim fills (or None).
"""
import re

PERCENT = re.compile(r"(\d{1,3})\s?(?:%|percent|per cent)")


def _percents(text):
    return [int(p) for p in PERCENT.findall(text) if int(p) <= 100]


def _has(pattern):
    rx = re.compile(pattern, re.I)
    return lambda text: bool(rx.search(text))


FLAT = _has(r"\b(flat( out)?|full throttle (all the way )?through|no brak\w*|don'?t (need to )?brake|"
            r"without braking|foot to the floor)\b")
HARD_BRAKING = _has(r"\b(brak\w*|break\w*) (really )?(hard|heavily|heavy)|\bhard on the brakes|\bbig stop|"
                    r"\bheav(y|iest) brak\w*|\bmaximum (brake|braking)|\bfull (brake )?pressure|"
                    r"\bhardest brak\w*")
SLOW = _has(r"\b(slow(est)? (corner|speed|part)|first gear|1st gear|tight (corner|hairpin)|hairpin|"
            r"really slow|very slow)\b")
FAST = _has(r"\b(fast(est)? (corner|part|sweep\w*)|high[- ]speed|(fifth|sixth|5th|6th) gear|quick (corner|left|right))\b")


def text_of(note):
    return " ".join(str(v) for v in note.values() if v)


def _brake_percents(note):
    """Brake pressures said about braking (not throttle percentages on exit)."""
    return _percents(note.get("braking") or "")


def _heavy_braking(note):
    text = text_of(note)
    if HARD_BRAKING(text) or any(p >= 60 for p in _brake_percents(note)):
        return "confirm"
    if FLAT(text) and not note.get("braking"):
        return "contradict"
    return None


def _flat_out(note):
    text = text_of(note)
    if any(p >= 40 for p in _brake_percents(note)) or HARD_BRAKING(text):
        return "contradict"
    return "confirm" if FLAT(text) else None


def _word(confirm, contradict=None):
    yes, no = _has(confirm), _has(contradict) if contradict else (lambda _: False)
    return lambda note: "confirm" if yes(text_of(note)) else "contradict" if no(text_of(note)) else None


def _either(confirm, contradict):
    return lambda note: "confirm" if confirm(text_of(note)) else "contradict" if contradict(text_of(note)) else None


def _metric(confirm, contradict):
    def test(m):
        if not m:
            return None
        if confirm(m):
            return "confirm"
        if contradict(m):
            return "contradict"
        return None
    return test


CLAIMS = {
    "heavy_braking": {
        "statement": "Heavy braking zone",
        "transcript": _heavy_braking,
        "telemetry": _metric(lambda m: m["peak_brake"] >= 0.6 and m.get("speed_drop", 0) >= 0.25,
                             lambda m: m["peak_brake"] < 0.15),
        "approach_dependent": True, "coach_field": ("brake_type", "HEAVY"),
    },
    "flat_out": {
        "statement": "Taken flat, no braking",
        "transcript": _flat_out,
        "telemetry": _metric(lambda m: m["peak_brake"] < 0.1 and m["min_throttle"] >= 0.9,
                             lambda m: m["peak_brake"] >= 0.4),
        "approach_dependent": True, "coach_field": ("brake_type", "NONE"),
    },
    "slow_corner": {
        "statement": "Slow corner",
        "transcript": _either(SLOW, FLAT),
        "telemetry": _metric(lambda m: m["min_speed_share"] <= 0.45, lambda m: m["min_speed_share"] >= 0.7),
        "approach_dependent": False, "coach_field": ("corner_type", "SLOW"),
    },
    "fast_corner": {
        "statement": "Fast corner",
        "transcript": _either(lambda t: FAST(t) or FLAT(t), SLOW),
        "telemetry": _metric(lambda m: m["min_speed_share"] >= 0.7, lambda m: m["min_speed_share"] <= 0.45),
        "approach_dependent": False, "coach_field": ("corner_type", "FAST"),
    },
    "hairpin": {
        "statement": "Hairpin",
        "transcript": _word(r"\bhairpin\b"),
        "telemetry": _metric(lambda m: m["min_speed_share"] <= 0.35, lambda m: m["min_speed_share"] >= 0.6),
        "approach_dependent": False, "coach_field": ("corner_type", "HAIRPIN"),
    },
    "chicane": {
        "statement": "Chicane",
        "transcript": _word(r"\bchicane\b"),
        "telemetry": None, "approach_dependent": False, "coach_field": ("corner_type", "CHICANE"),
    },
    "important_exit": {
        "statement": "Exit leads onto a long full-throttle run; exit speed matters",
        "transcript": _word(r"\b(exit (is|is really|is so|is very) (important|key|crucial|critical)|long straight|"
                            r"(good|strong|clean) exit|carry (the |that )?speed (down|onto|out|along)|"
                            r"onto the (back |main |front )?straight|down the (back |main |front )?straight)\b"),
        "telemetry": _metric(lambda m: m["flat_after_pct"] >= 0.08, lambda m: m["flat_after_pct"] < 0.02),
        "approach_dependent": True, "coach_field": ("importance", "HIGH"),
    },
    "overtaking_zone": {
        "statement": "Overtaking opportunity",
        "transcript": _word(r"\b(overtak\w*|make (a|the) pass|passing (zone|opportunit\w*|spot)|"
                            r"dive (bomb|up the inside)|send it up the inside|good place to pass)\b"),
        "telemetry": None, "approach_dependent": True, "coach_field": None,
    },
    "elevation_change": {
        "statement": "Elevation change (crest, compression, uphill or downhill)",
        "transcript": _word(r"\b(uphill|downhill|crest|compression|elevation|blind|drops? away|over the (hill|rise)|"
                            r"up the hill|down the hill)\b"),
        "telemetry": None, "approach_dependent": False, "coach_field": None,
    },
    "banked": {
        "statement": "Banked corner",
        "transcript": _word(r"\bbank(ed|ing)\b"),
        "telemetry": None, "approach_dependent": False, "coach_field": None,
    },
}
