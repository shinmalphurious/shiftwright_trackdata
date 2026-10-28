"""Braking landmarks and lap timing per layout, from real telemetry.

Sources (read-only):
- the Shiftwright database (SHIFTWRIGHT_DB, default ../Project_Shiftwright/shiftwright.db):
  the driver's own laps in telemetry_samples;
- reference lap traces (CSV with LapDistPct, Brake, Speed) under
  $SHIFTWRIGHT_DATA_ROOT/references/<car>/<track_id>/*.csv.

For a layout it returns, from up to MAX_LAPS laps:
- braking_turns: turn labels that a braking zone leads into in at least half of the laps
  (each braking zone belongs to the first turn after where it starts);
- elapsed: [(lap_pct, seconds since the line)] for one lap, to convert time to lap position.
Returns None when there is no telemetry for the layout.
"""
import csv
import os
import sqlite3
from functools import lru_cache
from pathlib import Path

from src.shared.paths import DATA_ROOT, REPO_ROOT

DB = Path(os.environ.get("SHIFTWRIGHT_DB") or REPO_ROOT.parent / "Project_Shiftwright" / "shiftwright.db")
REFERENCES = DATA_ROOT / "references"

BRAKE_ON = 0.2           # brake pedal share that starts a braking zone
MIN_ZONE_PCT = 0.002     # shorter brake applications are ignored (a dab, a pedal bump)
LEAD_IN_PCT = 0.12       # a zone belongs to a turn at most this far ahead of where it starts
MAX_LAPS = 8


def _zones(samples):
    """Lap pct where each braking zone starts. samples: [(pct, brake)] sorted by pct."""
    starts, start, last = [], None, None
    for pct, brake in samples:
        if brake >= BRAKE_ON:
            if start is None:
                start = pct
            last = pct
        elif start is not None:
            if last - start >= MIN_ZONE_PCT:
                starts.append(start)
            start = None
    if start is not None and last - start >= MIN_ZONE_PCT:
        starts.append(start)
    return starts


def _elapsed(samples):
    """[(pct, seconds)] from [(pct, t_or_None, speed_mps)]: uses timestamps when present, else
    integrates distance over speed (needs the lap length, so returns shares of the lap time)."""
    out, total = [], 0.0
    prev = None
    for pct, t, speed in samples:
        if prev is not None:
            if t is not None and prev[1] is not None:
                total += max(t - prev[1], 0.0)
            else:
                total += max(pct - prev[0], 0.0) / max(speed, 1.0)
        out.append((pct, total))
        prev = (pct, t)
    return out


def _db_laps(track_id):
    if not DB.exists():
        return []
    try:
        con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    except sqlite3.Error:
        return []
    try:
        lap_ids = [r[0] for r in con.execute(
            """SELECT l.id FROM laps l JOIN sessions s ON s.id = l.session_id
               LEFT JOIN lap_summaries ls ON ls.lap_id = l.id
               WHERE s.track_id = ? AND COALESCE(ls.valid, 1) = 1 AND COALESCE(ls.lap_type, 'FLYING') = 'FLYING'
               ORDER BY l.lap_time LIMIT ?""", (track_id, MAX_LAPS))]
        laps = []
        for lap_id in lap_ids:
            rows = con.execute("SELECT lap_dist_pct, brake, timestamp, speed, throttle FROM telemetry_samples "
                               "WHERE lap_id = ? ORDER BY timestamp", (lap_id,)).fetchall()
            rows = [r for r in rows if r[0] is not None]
            if len(rows) > 200:
                laps.append([(r[0], r[1] or 0.0, r[2], r[3] or 0.0, r[4] or 0.0) for r in rows])
        return laps
    except sqlite3.Error:
        return []
    finally:
        con.close()


def _reference_laps(track_id):
    laps = []
    for path in sorted(REFERENCES.glob(f"*/{track_id}/*.csv"))[:MAX_LAPS]:
        with open(path, encoding="utf-8") as f:
            rows = [(float(r["LapDistPct"]), float(r.get("Brake") or 0), None, float(r.get("Speed") or 0),
                     float(r.get("Throttle") or 0))
                    for r in csv.DictReader(f) if r.get("LapDistPct")]
        if len(rows) > 200:
            laps.append(rows)
    return laps


def coverage():
    """{track_id: {"laps": own laps with telemetry, "references": reference traces}} without
    loading samples. The same sources landmarks() reads, so anything counted here is used."""
    out = {}
    if DB.exists():
        try:
            con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
            try:
                for track_id, laps in con.execute(
                        """SELECT s.track_id, COUNT(DISTINCT l.id) FROM sessions s
                           JOIN laps l ON l.session_id = s.id
                           WHERE EXISTS (SELECT 1 FROM telemetry_samples t WHERE t.lap_id = l.id)
                           GROUP BY s.track_id"""):
                    out.setdefault(track_id, {"laps": 0, "references": 0})["laps"] = laps
            finally:
                con.close()
        except sqlite3.Error:
            pass
    for path in REFERENCES.glob("*/*/*.csv"):
        if path.parent.name.isdigit():
            entry = out.setdefault(int(path.parent.name), {"laps": 0, "references": 0})
            entry["references"] += 1
    return out


@lru_cache(maxsize=64)
def landmarks(track_id, turns):
    """turns: tuple of (label, lap_pct) in lap order. See module docstring."""
    laps = _db_laps(track_id) + _reference_laps(track_id)
    if not laps or not turns:
        return None
    votes = {}
    for lap in laps:
        ordered = sorted((s[0], s[1]) for s in lap)
        braked = set()
        for start in _zones(ordered):
            ahead = [(((pct - start) % 1.0), label) for label, pct in turns]
            distance, label = min(ahead)
            if distance <= LEAD_IN_PCT:
                braked.add(label)
        for label in braked:
            votes[label] = votes.get(label, 0) + 1
    braking = {label for label, n in votes.items() if n * 2 >= len(laps)}
    # Lap timing from the first lap that has it (a reference lap or the driver's best)
    timed = sorted((s[0], s[2], s[3]) for s in laps[0])
    return {"laps": len(laps), "braking_turns": braking, "elapsed": _elapsed(timed)}


def time_to_pct(elapsed, pct_a, pct_b, fraction):
    """The lap pct between pct_a and pct_b reached after `fraction` of the time the lap takes
    from pct_a to pct_b. Slow corners take longer, so this beats a straight line."""
    def at(pct):
        for (p0, t0), (p1, t1) in zip(elapsed, elapsed[1:]):
            if p0 <= pct <= p1:
                return t0 + (t1 - t0) * ((pct - p0) / (p1 - p0) if p1 > p0 else 0)
        return elapsed[-1][1] if pct > elapsed[-1][0] else 0.0
    ta, tb = at(pct_a), at(pct_b)
    target = ta + fraction * (tb - ta)
    for (p0, t0), (p1, t1) in zip(elapsed, elapsed[1:]):
        if t0 <= target <= t1 and pct_a <= p1 and p0 <= pct_b:
            return p0 + (p1 - p0) * ((target - t0) / (t1 - t0) if t1 > t0 else 0)
    return pct_a + fraction * (pct_b - pct_a)


def _between(samples, lo, hi):
    """Samples with lo <= pct <= hi, wrapping past the line when lo > hi or outside [0, 1]."""
    lo, hi = lo % 1.0, hi % 1.0
    if lo <= hi:
        return [s for s in samples if lo <= s[0] <= hi]
    return [s for s in samples if s[0] >= lo or s[0] <= hi]


def _median(values):
    values = sorted(v for v in values if v is not None)
    if not values:
        return None
    mid = len(values) // 2
    return values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2


@lru_cache(maxsize=64)
def corner_metrics(track_id, turns):
    """Per turn, medians over the available laps:
        peak_brake     strongest brake application leading into the turn (0..1)
        speed_drop     share of speed lost from the approach to the slowest point
        min_speed_share slowest speed near the turn as a share of the lap's top speed
        min_throttle   least throttle around the apex (1 = flat out)
        flat_after_pct share of the lap driven at full throttle after the turn, before the next braking
    turns: tuple of (label, lap_pct) in lap order. Returns {"laps": n, "cars": [...], "turns": {label: {...}}}
    or None without telemetry."""
    laps = _db_laps(track_id) + _reference_laps(track_id)
    if not laps or not turns:
        return None
    per_turn = {label: [] for label, _ in turns}
    pcts = [p for _, p in turns]
    for lap in laps:
        samples = sorted(lap)
        top = max((s[3] for s in samples), default=0) or 1.0
        for i, (label, p) in enumerate(turns):
            previous = pcts[i - 1] if i else pcts[-1] - 1.0
            lead_from = max(p - LEAD_IN_PCT, (previous + p) / 2)
            lead = _between(samples, lead_from, p + 0.01)
            near = _between(samples, p - 0.02, p + 0.02)
            if not lead or not near:
                continue
            entry = max(s[3] for s in _between(samples, lead_from, p)) if _between(samples, lead_from, p) else None
            slowest = min(s[3] for s in near)
            flat = 0.0
            after = sorted(_between(samples, p, p + 0.5), key=lambda s: (s[0] - p) % 1.0)
            started = False
            for s in after:
                if s[4] >= 0.95 and s[1] < 0.05:
                    if not started:
                        started, start_pct = True, s[0]
                    flat = (s[0] - start_pct) % 1.0
                elif started:
                    break
            per_turn[label].append({
                "peak_brake": max(s[1] for s in lead),
                "speed_drop": 1 - slowest / entry if entry else None,
                "min_speed_share": slowest / top,
                "min_throttle": min(s[4] for s in _between(samples, p - 0.02, p + 0.01)),
                "flat_after_pct": flat,
            })
    out = {}
    for label, rows in per_turn.items():
        if rows:
            out[label] = {key: round(_median([r[key] for r in rows]), 3) for key in rows[0]
                          if _median([r[key] for r in rows]) is not None}
            out[label]["laps"] = len(rows)
    return {"laps": len(laps), "turns": out}
