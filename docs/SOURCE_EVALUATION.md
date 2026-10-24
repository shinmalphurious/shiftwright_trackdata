# Track Knowledge Source Evaluation

## Goal

Build a sustainable source of:

- Elevation profiles
- Camber awareness
- Corner characteristics
- Track descriptions
- Driving implications

without relying on driver telemetry.

---

# Candidate Sources

## SVG Assets

Status: Available

Strengths:

- Corner ordering
- Geometry
- Radius estimation
- Straight lengths

Weaknesses:

- No elevation
- No camber
- No corner descriptions

Useful For:

Track Structure

Confidence:

HIGH

---

## OpenStreetMap

Status: Investigate

Potential:

- Geolocation
- Track centerlines
- Track segmentation

Unknown:

- Circuit completeness
- Accuracy

Useful For:

Track Characteristics

Confidence:

MEDIUM

---

## Digital Elevation Models

Candidates:

- SRTM
- Copernicus DEM

Potential:

- Elevation profile
- Gradient
- Crests
- Compression zones

Useful For:

Track Characteristics

Confidence:

HIGH

---

## Circuit Documentation

Candidates:

- FIA
- Circuit Websites
- RacingCircuits.info

Potential:

- Corner names
- Official descriptions

Useful For:

Track Knowledge

Confidence:

MEDIUM

---

## Driver Guides

Candidates:

- Driver61
- Track Titan
- Coach Dave

Potential:

- Braking zones
- Common mistakes
- Coaching information

Useful For:

Track Knowledge

Confidence:

LOW-MEDIUM

Requires review.

---

# Layer Ownership

## Track Structure

Source:

SVG

Examples:

- Corner order
- Shape
- Radius

---

## Track Characteristics

Sources:

SVG
+
Elevation

Examples:

- Hairpin
- Chicane
- Fast sweeper
- Uphill braking zone
- Downhill entry

---

## Track Knowledge

Sources:

Human-authored
Documentation

Examples:

- Common mistakes
- Typical coaching advice
- Driver notes

---

# Immediate Research Tasks

1. Evaluate OpenStreetMap coverage.
2. Evaluate elevation datasets.
3. Determine whether elevation can be mapped to track geometry.
4. Determine whether corner descriptions can be sourced legally.