# Track Knowledge Architecture

## External Dependencies

### Racing Track Maps Vector Repository

Location:

```text
E:\Project_Shiftwright\external\racing-track-maps-vector
```

Primary source of:

```text
Track Geometry
Track Layouts
SVG Track Ribbons
Track Variants
```

---

### Lovely Racing Repository

Location:

```text
E:\Project_Shiftwright\...
```

Primary source of:

```text
Named Corners
Corner Metadata
Corner Lengths
Track Metadata
```

Lovely is an enrichment source.

The geometry pipeline remains functional without Lovely.

---

# Geometry Pipeline

### src/geometry/skeleton_generator.py

```text
SVG Ribbon
    ↓
Skeleton
```

---

### src/geometry/centreline_extractor.py

```text
Skeleton
    ↓
Ordered Centreline
```

---

### src/pipelines/build_axis_library.py

```text
Centreline
    ↓
Axis Library
```

Output:

```text
generated/axis_registry.json
```

Coverage:

```text
424 tracks
2048 centreline samples per track
```

---

### src/geometry/curvature_analyzer.py

```text
Axis
    ↓
Curvature Profile
```

---

# Corner Detection Pipeline

### src/pipelines/build_corner_candidate_library.py

```text
Curvature
    ↓
Corner Candidates
```

---

### src/pipelines/build_corner_apex_library.py

```text
Corner Candidates
    ↓
Corner Apexes
```

---

### src/pipelines/build_corner_region_library.py

```text
Corner Apexes
    ↓
Corner Regions
```

Output:

```text
generated/corner_regions/*.json
```

Corner Region Structure:

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

# Track Knowledge Pipeline

### src/pipelines/build_knowledge_registry.py

Inputs:

```text
generated/*.json
generated/corner_regions/*.json
```

Output:

```text
generated/knowledge_registry.json
```

Knowledge Levels:

```text
direct
inherited
geometry_only
```

---

### src/pipelines/build_enriched_tracks.py

Inputs:

```text
Lovely Corner Data
Corner Dependencies
Corner Characteristics
```

Output:

```text
generated/enriched_tracks/*.json
```

Provides:

```text
Named Corners
Corner Characteristics
Corner Relationships
```

---

### src/models/track_knowledge.py

```text
Track Knowledge Data Models
```

---

### src/corners/track_insights.py

```text
Corner Classification Logic
```

---

### src/pipelines/build_track_knowledge_pack.py

Inputs:

```text
Track Models
Knowledge Registry
Corner Regions
Track Catalog
```

Output:

```text
generated/knowledge_packs/*.json
```

Coverage:

```text
424 tracks
```

---

# YouTube Knowledge Pipeline

### src/youtube/segment_turn_ranges.py

```text
Transcripts
    ↓
Turn Segments
```

Output:

```text
research/youtube/turn_ranges.csv
```

---

### src/youtube/extract_turn_facts_v2.py

```text
Turn Segments
    ↓
Structured Facts
```

Output:

```text
research/youtube/turn_facts_v2.csv
```

---

### src/youtube/build_track_turn_consensus.py

```text
Turn Facts
    ↓
Corner Consensus
```

Provides:

```text
Corner Coaching Knowledge
Community Techniques
Corner Characteristics
```

---

### src/youtube/build_track_fact_summary.py

```text
Turn Facts
    ↓
Track Summary
```

Provides:

```text
Track Themes
Driving Characteristics
Common Coaching Advice
```

---

# Platform Infrastructure

### src/pipelines/build_track_catalog.py

Output:

```text
generated/track_catalog.json
```

Provides:

```text
Track Discovery
Track Layout Metadata
Track Asset Coverage
```

---

### src/pipelines/build_acquisition_registry.py

Output:

```text
generated/acquisition_registry.json
```

Provides:

```text
Knowledge Acquisition Status
Coverage Tracking
```

---

# Core Data Flow

```text
Racing Track Maps Vector SVGs
                ↓

skeleton_generator.py
                ↓

centreline_extractor.py
                ↓

build_axis_library.py
                ↓

Axis Library
                ↓

curvature_analyzer.py
                ↓

build_corner_candidate_library.py
                ↓

build_corner_apex_library.py
                ↓

build_corner_region_library.py
                ↓

generated/corner_regions/*.json
                ↓

build_knowledge_registry.py
                ↓

knowledge_registry.json
                ↓

build_track_knowledge_pack.py
                ↓

knowledge_packs/*.json


Lovely Racing
        ↓

build_enriched_tracks.py
        ↓

Named Corners
Corner Metadata
Track Metadata


YouTube Transcripts
        ↓

segment_turn_ranges.py
        ↓

extract_turn_facts_v2.py
        ↓

build_track_turn_consensus.py
build_track_fact_summary.py
        ↓

Track Knowledge
Corner Knowledge
        ↓

knowledge_packs/*.json
```

skeleton_generator.py
        ↓
centreline_extractor.py
        ↓
build_axis_library.py
        ↓
normalize_axis_library.py
        ↓
build_axis_registry.py
        ↓

curvature_peak_detector.py
        ↓
build_corner_candidate_library.py
        ↓
build_corner_apex_library.py
        ↓

corner_region_detector.py
region_deduplicator.py
        ↓

build_corner_region_library.py
        ↓
generated/corner_regions
        ↓

build_corner_metrics_library.py
        ↓

characteristics.py
corner_dependency.py
        ↓

build_corner_characteristics_library.py
build_corner_dependency_library.py
        ↓

build_enriched_tracks.py
        ↓

build_knowledge_registry.py
        ↓

build_track_knowledge_pack.py