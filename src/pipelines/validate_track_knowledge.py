"""Check the inputs of the knowledge packs before they are built.

Reads generated/turn_markers/<id>.json, the named corners in generated/<id>.json and
config/corner_aliases.json. Reports, per layout:
    duplicate_turn_id         a turn label appears on more than one marker
    missing_turn_number       a number is skipped between T1 and the highest turn (T10, T12)
    non_sequential_order      a turn lies before a lower-numbered turn on the lap
    named_corner_repeats_label a named corner lists the same turn twice (usually a misread marker)
    alias_collision           one alias phrase points to two corners of the layout
    ambiguous_alias           an alias is a generic word speakers use for many corners
    invalid_reference         an alias points to a turn the layout does not have, or names a
                              layout that has no turn markers
Warnings do not stop the build: enrich_corner_assignments already drops duplicate markers and
colliding aliases. They point at source data to fix.

Writes generated/validation/track_knowledge_validation.json. build_track_knowledge_pack runs
this first.

Usage: python -m src.pipelines.validate_track_knowledge
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared.iracing_tracks import load_layouts
from src.shared.paths import GENERATED, REPO_ROOT

OUT = GENERATED / "validation" / "track_knowledge_validation.json"
ALIASES = REPO_ROOT / "config" / "corner_aliases.json"
# Words speakers use for several corners of the same track
AMBIGUOUS = {"banking", "banked", "hairpin", "chicane", "esses", "the esses", "kink", "the kink", "carousel",
             "straight", "back straight", "bridge", "dip", "crest", "sweeper", "the loop", "loop", "bowl",
             "corner", "turn", "bend", "curve", "apex", "braking zone", "last corner", "first corner"}


def _json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def named_labels(corners, markers):
    """Labels inside each named corner's lap range, as build_track_knowledge_pack assigns them."""
    turns = markers.get("turns", [])
    out = []
    for corner in corners:
        start, end = corner.get("start_pct"), corner.get("end_pct")
        labels = [t["label"] for t in turns if markers.get("direction_known") and start is not None
                  and end is not None and start <= t["lap_pct"] <= end]
        if corner.get("name"):
            out.append((corner["name"], labels))
    return out


def validate(track_id, markers, corners, config):
    issues = []
    turns = markers.get("turns", [])
    labels = Counter(t["label"] for t in turns)
    for label, count in labels.items():
        if count > 1:
            issues.append({"issue": "duplicate_turn_id", "turn_id": label, "markers": count,
                           "lap_pct": [t["lap_pct"] for t in turns if t["label"] == label]})
    numbers = sorted({int(m.group(1)) for l in labels for m in [re.fullmatch(r"T(\d+)", l)] if m})
    if numbers:
        missing = [n for n in range(1, numbers[-1] + 1) if n not in numbers]
        if missing:
            issues.append({"issue": "missing_turn_number", "turn_ids": [f"T{n}" for n in missing]})
    if markers.get("direction_known"):
        unique = sorted(((int(t["label"][1:]), t["lap_pct"]) for t in turns
                         if labels[t["label"]] == 1 and re.fullmatch(r"T\d+", t["label"])))
        steps = list(zip(unique, unique[1:]))
        # Going backwards: not the wrap past the start/finish line, not two markers on one spot
        backwards = [((n1, p1), (n2, p2)) for (n1, p1), (n2, p2) in steps
                     if p2 < p1 - 0.005 and not (p1 >= 0.8 and p2 <= 0.2)]
        if steps and len(backwards) * 2 > len(steps):
            issues.append({"issue": "non_sequential_order", "detail": "most turns run backwards: lap direction "
                           "or numbering is reversed", "turns_backwards": len(backwards), "steps": len(steps)})
        else:
            for (n1, p1), (n2, p2) in backwards:
                issues.append({"issue": "non_sequential_order", "turn_ids": [f"T{n1}", f"T{n2}"],
                               "lap_pct": [p1, p2]})
    for name, named in named_labels(corners, markers):
        repeated = [l for l, c in Counter(named).items() if c > 1]
        if repeated:
            issues.append({"issue": "named_corner_repeats_label", "corner": name, "turn_ids": named})

    claims = defaultdict(set)
    for name, named in named_labels(corners, markers):
        if len(set(named)) == 1:
            claims[name.lower()].add(named[0])
    layout_aliases = config.get("layouts", {}).get(str(track_id), {})
    for label, phrases in layout_aliases.items():
        if label.startswith("_"):
            continue
        if label not in labels:
            issues.append({"issue": "invalid_reference", "turn_id": label, "aliases": phrases,
                           "detail": "alias for a turn this layout does not have"})
        for phrase in phrases:
            claims[phrase.lower()].add(label)
            if phrase.lower() in AMBIGUOUS:
                issues.append({"issue": "ambiguous_alias", "alias": phrase, "turn_id": label})
    for phrase, owners in claims.items():
        if len(owners) > 1:
            issues.append({"issue": "alias_collision", "alias": phrase, "turn_ids": sorted(owners)})
    return issues


def run(verbose=True):
    layouts = load_layouts()
    config = _json(ALIASES, {})
    report = {}
    for path in sorted((GENERATED / "turn_markers").glob("*.json"), key=lambda p: int(p.stem)):
        track_id = int(path.stem)
        markers = _json(path, {})
        corners = _json(GENERATED / f"{track_id}.json", {}).get("corners", [])
        issues = validate(track_id, markers, corners, config)
        if issues:
            report[track_id] = {"track": layouts.get(track_id, {}).get("name", str(track_id)), "issues": issues}
    for layout in config.get("layouts", {}):
        if not (GENERATED / "turn_markers" / f"{layout}.json").exists():
            report.setdefault(int(layout), {"track": layouts.get(int(layout), {}).get("name", layout), "issues": []})
            report[int(layout)]["issues"].append({"issue": "invalid_reference",
                                                  "detail": "aliases configured for a layout with no turn markers"})

    totals = Counter(i["issue"] for r in report.values() for i in r["issues"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"summary": dict(totals), "layouts_with_issues": len(report),
                               "layouts": {str(k): v for k, v in sorted(report.items())}},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    if verbose:
        print(f"validation: {len(report)} layouts with warnings  {dict(totals)}  -> {OUT.relative_to(REPO_ROOT)}")
    return report


if __name__ == "__main__":
    report = run()
    for track_id, entry in sorted(report.items()):
        for issue in entry["issues"]:
            detail = {k: v for k, v in issue.items() if k != "issue"}
            print(f"  {track_id:4} {entry['track'][:40]:40} {issue['issue']:28} {detail}")
