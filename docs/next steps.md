# Next Steps

## Current State

The foundational pipeline is complete.

Current coverage:

```text
Tracks:               424
Knowledge Packs:      424
Axis Models:          424
Corner Regions:       424

Direct Knowledge:      78
Inherited Knowledge:   61
Geometry Only:        285
```

Current architecture:

```text
SVG
↓
Skeleton
↓
Centreline
↓
Axis
↓
Corner Regions
↓
Knowledge Registry
↓
Knowledge Packs

+

Lovely
↓
Named Corners

+

YouTube
↓
Track Knowledge
↓
Corner Knowledge
```

---

# Immediate Priority

Focus on improving the YouTube extraction pipeline.

Current output:

```text
52 turn segments
↓
9 fact records
```

The information exists but most of it is being discarded.

Current extracted concepts:

```text
braking_zone
trail_braking
apex_focus
exit_focus
long_straight
flat_corner
hairpin
cambered
slippery
```

---

# Next Development Goal

Move from:

```text
Fact Extraction
```

to:

```text
Evidence Extraction
```

Current:

```json
{
  "fact": "slippery"
}
```

Target:

```json
{
  "fact": "slippery",
  "evidence": [
    "This corner is incredibly slippery.",
    "Very slippy on exit."
  ]
}
```

Store supporting transcript evidence.

---

# Knowledge Pack Integration

Knowledge packs currently contain:

```json
{
  "track_id": 41,
  "knowledge_level": "geometry_only",
  "named_corners": [],
  "generated_corner_regions": [],
  "knowledge_registry": {},
  "track_catalog": {}
}
```

Future enrichment should populate:

```json
{
  "youtube_summary": {},
  "turn_consensus": {}
}
```

from:

```text
build_track_fact_summary.py
build_track_turn_consensus.py
```

instead of leaving them empty.

---

# Core Investigation Remaining

Question:

```text
Why do 285 tracks remain geometry_only?
```

Current facts:

```text
Lovely With Corners      78
Inherited With Corners   61
Geometry Only           285
```

Need to investigate whether:

```text
Inheritance can be expanded
```

or:

```text
Corner naming can be derived from additional sources.
```

---

# Future Knowledge Sources

Already planned:

```text
YouTube
Garage61
Telemetry
Car Datasheets
Lovely
```

Knowledge packs should become the canonical storage format for all enrichment.

---

# Current Knowledge Pack Structure

```text
track_id
knowledge_level
named_corners
generated_corner_regions
knowledge_registry
track_catalog
```

This model is considered stable.

New enrichment should attach here rather than creating additional disconnected artifacts.

---

# Primary Objective

Build a richer track knowledge repository.

The goal is not:

```text
Keywords
```

The goal is:

```text
Track Knowledge
↓
Corner Knowledge
↓
Supporting Evidence
↓
LLM Interpretation
```

The next engineering work should focus on increasing the amount and quality of knowledge entering the packs rather than creating additional infrastructure.