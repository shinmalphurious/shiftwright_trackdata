"""Track axis from iRacing's active.svg: the centre of the drawn track ribbon, as one closed loop.

active.svg draws the track as a filled ribbon: an outer outline and an inner outline (sub-paths).
The old extraction joined both outlines into one polygon, which filled parts of the infield, and
ordered skeleton pixels by nearest-neighbour hops, which jumped across gaps. Both produced chords
across the infield (e.g. Spa, Snetterton).

Here:
1. ribbon_mask: every sub-path is filled and combined even-odd (outer minus inner);
2. the mask is thinned to a one-pixel skeleton and dead-end branches (spurs) are pruned;
3. trace_loop walks the remaining loop pixel by pixel, at junctions continuing in the straightest
   direction (so a crossover such as a figure-of-eight is followed straight through), and the
   pixel staircase is smoothed along the loop (SMOOTH_PX; measured against GPS laps, 15 px gave
   the best lap-distance fit: Spa 6.6 m, Red Bull Ring 4.5 m, Le Mans 11.7 m median);
4. axis_quality measures the result against the ribbon: points off the track and share of the
   track the axis covers. The pipeline publishes an axis only when it passes.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, convolve, distance_transform_edt
from skimage.morphology import skeletonize
from svgpathtools import svg2paths

W, H = 1920, 1080
NEIGHBOURS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]   # (dy, dx)

MAX_OFF_TRACK_SHARE = 0.02     # at most 2 % of axis points more than 3 px outside the ribbon
MIN_COVERAGE = 0.95            # the axis must pass within 6 px of 95 % of the skeleton
SMOOTH_PX = 15


def ribbon_mask(svg_file, samples: int = 4000) -> np.ndarray:
    paths, _ = svg2paths(str(svg_file))
    mask = np.zeros((H, W), dtype=bool)
    for path in paths:
        if path.length() == 0:
            continue
        for sub in path.continuous_subpaths():
            if sub.length() < 1:
                continue
            img = Image.new("L", (W, H), 0)
            pts = [sub.point(i / (samples - 1)) for i in range(samples)]
            ImageDraw.Draw(img).polygon([(p.real, p.imag) for p in pts], fill=255)
            mask ^= np.array(img) > 0                      # even-odd fill
    return mask


def _degree(skel: np.ndarray) -> np.ndarray:
    kernel = np.ones((3, 3), dtype=int)
    kernel[1, 1] = 0
    return convolve(skel.astype(int), kernel, mode="constant") * skel


def prune_spurs(skel: np.ndarray, max_iter: int = 4000) -> np.ndarray:
    """Remove dead-end branches; loops (the track) remain."""
    skel = skel.copy()
    for _ in range(max_iter):
        ends = (_degree(skel) <= 1) & skel
        if not ends.any():
            break
        skel[ends] = False
    return skel


def trace_loop(skel: np.ndarray, heading_len: int = 6) -> np.ndarray:
    """Ordered (x, y) points around the skeleton loop, starting at its leftmost pixel."""
    ys, xs = np.nonzero(skel)
    if len(xs) < 20:
        raise ValueError("skeleton too small")
    on = set(zip(ys.tolist(), xs.tolist()))
    start = min(on, key=lambda p: (p[1], p[0]))
    degree = _degree(skel)
    path = [start]
    visits = {start: 1}
    prev = None
    current = start
    limit = 3 * len(on)
    while len(path) < limit:
        candidates = [(current[0] + dy, current[1] + dx) for dy, dx in NEIGHBOURS]
        candidates = [c for c in candidates if c in on and c != prev]
        # each pixel once, junction pixels (a crossover) at most twice
        candidates = [c for c in candidates if visits.get(c, 0) < (2 if degree[c] >= 3 else 1)
                      or (c == start and len(path) > 50)]
        if not candidates:
            break
        if len(path) > heading_len:
            back = path[-heading_len]
            heading = np.array([current[0] - back[0], current[1] - back[1]], dtype=float)
        else:
            heading = None
        if heading is not None and np.any(heading):
            heading /= np.linalg.norm(heading)
            def turn(c):
                step = np.array([c[0] - current[0], c[1] - current[1]], dtype=float)
                return -float(step @ heading) / np.linalg.norm(step)
            candidates.sort(key=turn)
        else:   # first steps: prefer 4-connected neighbours so the walk starts along the line
            candidates.sort(key=lambda c: abs(c[0] - current[0]) + abs(c[1] - current[1]))
        nxt = candidates[0]
        if nxt == start:
            break
        prev, current = current, nxt
        path.append(current)
        visits[current] = visits.get(current, 0) + 1
    pts = np.array([(x, y) for y, x in path], dtype=float)
    if len(pts) < 20 or np.hypot(*(pts[-1] - pts[0])) > 3:
        raise ValueError("loop did not close")
    return pts


def smooth_loop(pts: np.ndarray, window: int = SMOOTH_PX) -> np.ndarray:
    """Moving average along a closed loop (removes the 8-connected pixel staircase)."""
    if window <= 1:
        return pts
    kernel = np.ones(window) / window
    ext = np.vstack([pts[-window:], pts, pts[:window]])
    out = np.column_stack([np.convolve(ext[:, i], kernel, mode="same") for i in range(2)])
    return out[window:-window]


def axis_quality(mask: np.ndarray, axis: np.ndarray) -> dict:
    """Share of axis points more than 3 px off the ribbon; share of the ribbon's skeleton covered."""
    outside = distance_transform_edt(~mask)
    xi = np.clip(np.round(axis[:, 0]).astype(int), 0, W - 1)
    yi = np.clip(np.round(axis[:, 1]).astype(int), 0, H - 1)
    off = float((outside[yi, xi] > 3).mean())
    skel = skeletonize(mask)
    near = np.zeros_like(mask)
    near[yi, xi] = True
    near = binary_dilation(near, iterations=6)
    sy, sx = np.nonzero(skel)
    coverage = float(near[sy, sx].mean()) if len(sx) else 0.0
    return {"off_track_share": off, "coverage": coverage,
            "ok": off <= MAX_OFF_TRACK_SHARE and coverage >= MIN_COVERAGE}


def ribbon_axis(svg_file) -> tuple[np.ndarray, dict]:
    mask = ribbon_mask(svg_file)
    axis = smooth_loop(trace_loop(prune_spurs(skeletonize(mask))))
    return axis, axis_quality(mask, axis)
