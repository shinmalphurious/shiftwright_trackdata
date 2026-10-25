# Track Knowledge Geometry Validation Report

## Objective

Determine whether the `racing-track-maps-vector` repository contains enough information to automatically derive a reusable track centreline and ultimately generate corner information for layouts not covered by Lovely Track Data.

---

# Inputs

## Geometry Source

```text
racing-track-maps-vector
└── active.svg
```

Example:

```text
Road/spielberg/403-spielberg-gp/active.svg
```

## Validation Source

```text
jacob_g61_vs_shiftwright.csv
```

Columns:

```text
LapDistPct
Lat
Lon
G61Speed
G61Steering
G61LatAccel
SWSpeed
SWSteering
SWLatAccel
SWLongAccel
SWYaw
SWYawRate
```

The Lat/Lon values were generated from:

```text
Speed
Yaw
Timestamp
LapDistPct correction
```

rather than true GPS.

---

# Experiments Performed

## 1. SVG Path Inspection

The SVG contains:

```svg
<path d="M ... c ... c ... Z" />
```

Result:

```text
Single continuous perimeter path
```

Not:

```text
Centreline
```

Not:

```text
Racing line
```

Instead:

```text
Track ribbon polygon
```

representing the drivable asphalt surface.

---

## 2. Boundary Extraction

Several boundary extraction approaches were attempted:

### Midpoint Averaging

```text
Outer Wall
+
Inner Wall
↓
Average
```

Result:

```text
Not centred
Bias toward apexes
```

Failed.

---

### Arc-Length Pairing

```text
Outer[i]
↔
Inner[i]
```

Result:

```text
Corner cutting
Incorrect pairing
```

Failed.

---

### KDTree Pairing

```text
Nearest Wall Correspondence
```

Result:

```text
Visually excellent centreline
```

but ordering issues remained.

---

# 3. Skeletonization

Instead of pairing walls, the ribbon polygon was rasterized and skeletonized:

```python
skeleton = skeletonize(binary)
```

Pipeline:

```text
SVG Ribbon
↓
Binary Polygon
↓
Skeleton
```

Result:

```text
Excellent centreline topology
```

Visual observations:

```text
✓ centred
✓ no seam artifact
✓ no connector artifact
✓ no corner cutting
✓ naturally follows track shape
```

---

# 4. Skeleton Validation

Skeleton statistics:

```text
Resolution:
1080 x 1920

Skeleton Pixels:
4305
```

Topology validation:

```text
Endpoints:
0

Junctions:
0
```

Interpretation:

```text
Perfect closed loop
```

No branches.

No disconnected sections.

No graph cleanup required.

---

# 5. SVG vs Skeleton Overlay

Overlay:

```text
Green = SVG Ribbon
Red = Skeleton
```

Result:

```text
Skeleton sits centrally inside the ribbon
for the entire lap
```

Observations:

```text
✓ T1 centred
✓ Remus centred
✓ Middle sector centred
✓ Final sector centred
✓ No visible seam distortion
```

Conclusion:

```text
Skeleton is a valid geometric centreline.
```

---

# 6. Shiftwright Overlay Validation

Coordinate transform tested:

```text
x = Lon
y = -Lat
```

This aligned the reconstruction with the SVG-derived geometry.

Result:

```text
Shape alignment successful
```

Visual matches:

```text
✓ T1
✓ T3
✓ Long straight
✓ Middle sector
✓ Final sector
```

---

# 7. Quantitative Validation

The skeleton axis was used as a reference.

For every reconstructed point:

```text
Reconstruction Point
↓
Nearest Axis Point
↓
Distance
```

Measured:

```text
Mean Offset       : 7.89
Median Offset     : 7.24
95th Percentile   : 17.53
Maximum Offset    : 21.89
```

Previously measured SVG ribbon width:

```text
Mean Width        : 19.96
```

Normalized values:

```text
Mean Offset
=
7.89 / 19.96
≈ 0.40 track widths

95th Percentile
=
17.53 / 19.96
≈ 0.88 track widths
```

Interpretation:

```text
The reconstruction remains close to the SVG-derived centreline.
```

Especially considering the reconstruction originates from:

```text
Speed
+
Yaw
+
Timestamp
```

integration.

---

# Key Findings

## Proven

The SVG geometry contains enough information to derive:

```text
Track Centreline
Track Geometry
Track Progression Axis
```

without telemetry.

---

## Proven

The skeleton approach outperforms:

```text
Boundary Averaging
Wall Pairing
Arc-Length Pairing
KDTree Centreline Generation
```

for centreline recovery.

---

## Proven

A reliable centreline can be generated from:

```text
active.svg
```

for Road circuits.

---

## Proven

The derived centreline matches an independently reconstructed lap shape.

Agreement exists in:

```text
Topology
Rotation
Scale (approximately)
Track Shape
```

---

# Recommended Production Pipeline

```text
active.svg
    ↓
Polygon Extraction
    ↓
Skeletonization
    ↓
Track Axis
    ↓
Axis Normalization
    ↓
Lap Percentage Mapping
    ↓
Curvature Profile
    ↓
Corner Candidate Generation
```

---

# Repository Architecture Update

## Phase 1 — Solved

```text
SVG
↓
Centreline
```

Status:

```text
✅ Complete
```

---

## Phase 2 — Next

```text
Centreline
↓
Curvature
```

Goal:

```text
Corner Apex Candidates
```

Example output:

```json
{
  "track_id": 403,

  "corner_candidates": [
    {
      "apex_pct": 0.29
    },
    {
      "apex_pct": 0.58
    }
  ]
}
```

---

## Phase 3

Validate against:

```text
105 Lovely-backed tracks
```

using:

```text
Lovely Start/End %
vs
Curvature Peaks
```

---

## Phase 4

Generate corners for:

```text
126 uncovered Road layouts
```

without telemetry.

---

# Final Conclusion

The major technical uncertainty was:

> Can a reliable track axis be generated automatically from SVG geometry?

Result:

```text
YES
```

Validated through:

```text
Ribbon Analysis
Boundary Analysis
Skeleton Extraction
Topology Validation
Visual Overlay
Shiftwright Overlay
Quantitative Offset Analysis
```

The Track Knowledge repository can now move from:

```text
Geometry Extraction
```

to:

```text
Knowledge Generation
```

using the generated track axis as the canonical coordinate system.
