# Architecture

## Track Discovery

### src/pipelines/build_track_catalog.py

**Input**

```text
E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing
```

**Output**

```text
generated/track_catalog.json
```

**Purpose**

```text
Discover all track layouts and track assets.
```

---

## Acquisition Tracking

### src/pipelines/build_acquisition_registry.py

**Input**

```text
generated/track_catalog.json
```

**Output**

```text
generated/acquisition_registry.json
```

**Purpose**

```text
Track enrichment status for each layout.
```

---

## YouTube Extraction

### src/youtube/segment_turn_ranges.py

**Input**

```text
research/youtube/transcripts/*.json
```

**Output**

```text
research/youtube/turn_ranges.csv
```

**Purpose**

```text
Transcript
    ↓
Turn Segments
```

---

### src/youtube/extract_turn_facts_v2.py

**Input**

```text
research/youtube/turn_ranges.csv
```

**Output**

```text
research/youtube/turn_facts_v2.csv
```

**Purpose**

```text
Turn Segment
    ↓
Structured Facts
```

---

## Track Knowledge Aggregation

### src/youtube/build_track_turn_consensus.py

**Input**

```text
research/youtube/turn_facts_v2.csv
```

**Output**

```text
Track + Turn Consensus
```

**Example**

```text
Zandvoort
    turn_10
        braking_zone
        cambered
        slippery
```

---

### src/youtube/build_track_fact_summary.py

**Input**

```text
research/youtube/turn_facts_v2.csv
```

**Output**

```text
Track Summary
```

**Example**

```text
Zandvoort
    braking_zone
    trail_braking
    cambered
```

---

## Corner Model

### src/pipelines/build_enriched_tracks.py

**Inputs**

```text
generated/*.json
generated/corner_dependencies/*.json
generated/corner_characteristics/*.json
```

**Output**

```text
generated/enriched_tracks/*.json
```

**Purpose**

```text
Corner Names
Corner Boundaries
Corner Characteristics
Corner Dependencies
```

---

### src/models/track_knowledge.py

**Purpose**

```text
Track knowledge data models.
```

---

### src/corners/track_insights.py

**Purpose**

```text
Corner insight classification logic.
```

---

# Current Pipeline

```text
SVG Repository
        ↓
build_track_catalog.py
        ↓
track_catalog.json
        ↓
build_acquisition_registry.py
        ↓
acquisition_registry.json


transcripts/*.json
        ↓
segment_turn_ranges.py
        ↓
turn_ranges.csv
        ↓
extract_turn_facts_v2.py
        ↓
turn_facts_v2.csv
                ├── build_track_turn_consensus.py
                └── build_track_fact_summary.py


Corner Data
        ↓
build_enriched_tracks.py
        ↓
enriched_tracks/*.json
```
## Corner Region Generation

### generated/corner_regions/*.json

Provides geometry-derived corner regions for all tracks.

Structure:

```text
start_pct
apex_pct
end_pct
strength
```

Coverage:

```text
424 tracks
```

---

## Corner Model

### src/pipelines/build_enriched_tracks.py

Inputs:

```text
generated/*.json
generated/corner_dependencies/*.json
generated/corner_characteristics/*.json
```

Output:

```text
gener*ted/enriched_tracks/*.json
```

Pu*pose:

```text
Corner Names
Corner*Boundaries
Corner Characteristics
*orner Dependencies
```

---

### s*c/models/track_knowledge.py

Purpo*e:

```text
Track knowledge data m*dels.
```

---

### src/corners/tr*ck_insights.py

Purpose:

```text
*orner insight classification logic*
```

---

## Knowledge Registry

*## src/pipelines/build_knowledge_r*gistry.py

Inputs:

```text
genera*ed/*.json
generated/corner_regions**.json
```

Output:

```text
gener*ted/knowledge_registry.json
```

P*rpose:

```text
Classify track kno*ledge coverage.

Levels:
    geome*ry_only
    direct
    inherited
`*`