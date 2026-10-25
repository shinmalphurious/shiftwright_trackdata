"""Align a closed SVG centreline to iRacing lap distance.

Raw axes start at an arbitrary point and may run backwards. Alignment:
start = point nearest the start/finish line; direction = the one in which
turn numbers from turns.svg increase.
"""
import re
import xml.etree.ElementTree as ET

import numpy as np
from svgpathtools import svg2paths

# turns.svg text anchors sit at the glyph's bottom-left (36px font).
_LABEL_OFFSET = np.array([10.0, -13.0])


def load_axis(csv_path):
    data = np.loadtxt(csv_path, delimiter=",", skiprows=1)
    return data[:, 1:3]


def start_finish_point(svg_path, axis):
    """Centroid of the start/finish sub-path that lies closest to the track."""
    best, best_dist = None, np.inf
    paths, _ = svg2paths(str(svg_path))
    for path in paths:
        for sub in path.continuous_subpaths():
            if sub.length() < 1e-6:
                continue
            pts = np.array([sub.point(t) for t in np.linspace(0, 1, 40)])
            pts = np.column_stack((pts.real, pts.imag))
            dist = np.mean(np.min(np.linalg.norm(pts[:, None] - axis[None], axis=2), axis=1))
            if dist < best_dist:
                best, best_dist = pts.mean(axis=0), dist
    return best


def turn_markers(svg_path):
    """[(number, x, y)] for numeric <text> labels in turns.svg."""
    markers = []
    for elem in ET.parse(svg_path).getroot().iter():
        if elem.tag.split("}")[-1] != "text":
            continue
        text = "".join(elem.itertext()).strip().upper().removeprefix("T")
        if not text.isdigit():
            continue
        nums = re.findall(r"[-+]?\d*\.?\d+", elem.attrib.get("transform", ""))
        if len(nums) >= 2:
            x, y = float(nums[-2]), float(nums[-1])
        elif "x" in elem.attrib and "y" in elem.attrib:
            x, y = float(elem.attrib["x"]), float(elem.attrib["y"])
        else:
            continue
        markers.append((int(text), *(np.array([x, y]) + _LABEL_OFFSET)))
    return sorted(markers)


def _pcts(axis, points):
    if not len(points):
        return np.array([])
    idx = np.argmin(np.linalg.norm(np.asarray(points)[:, None] - axis[None], axis=2), axis=1)
    return idx / len(axis)


def _order_score(pcts):
    return int(np.sum(np.diff(pcts) > 0))


def align(axis, sf_point, markers, points=1024):
    """Return (centreline[(pct,x,y)], turns[{label,number,x,y,lap_pct}], direction_known)."""
    if np.allclose(axis[0], axis[-1]):
        axis = axis[:-1]
    start = int(np.argmin(np.linalg.norm(axis - sf_point, axis=1)))
    forward = np.roll(axis, -start, axis=0)
    backward = np.roll(axis[::-1], -(len(axis) - 1 - start), axis=0)

    xy = [m[1:] for m in markers]
    f_score, b_score = _order_score(_pcts(forward, xy)), _order_score(_pcts(backward, xy))
    ordered = backward if b_score > f_score else forward
    direction_known = len(markers) >= 3 and f_score != b_score

    closed = np.vstack((ordered, ordered[:1]))
    seg = np.linalg.norm(np.diff(closed, axis=0), axis=1)
    cum = np.concatenate(([0.0], np.cumsum(seg))) / seg.sum()
    pct = np.linspace(0.0, 1.0, points + 1)
    line = np.column_stack((pct, np.interp(pct, cum, closed[:, 0]), np.interp(pct, cum, closed[:, 1])))

    turn_pcts = _pcts(line[:-1, 1:], xy)
    turns = [
        {"label": f"T{n}", "number": n, "x": round(x, 2), "y": round(y, 2), "lap_pct": round(float(p), 4)}
        for (n, x, y), p in zip(markers, turn_pcts)
    ]
    return line, turns, direction_known
