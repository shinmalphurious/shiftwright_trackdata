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

*orner Region Structure:

```text
s*art_pct
apex_pct
end_pct*strength
```

Coverage:

```text
4*4 tracks
```

*--

# Track Knowledge Pipeline

##* src/pipelines/build_knowledge*registry.py

Inputs:

```text
gene*ated/*.json
generated/corner_regio*s/*.json
```

Output:

```text*generated/knowledge*registry.json
```

Knowledge Level*:

```text
direct
inherited
geomet*y_only
```

*--

### src/pipelines/build_enrich*d_tracks.py

Inputs:

```text*Lovely Corner Data
Corner Dependen*ies
Corner Characteristics
``*

Output:

```text*generated/enriched_tracks/*.json
`*`

Provides:

```text
Named Corner*
Corner Characteristics
Corner Rel*tionships
```

*--

### src/models/track_knowledge*py

```text
Track Knowledge Data*Models
```

*--

### src/corners/track_insights*py

```text
Corner Classification *ogic
```

*--

###*src/pipelines/build_track_knowledg*_pack.py

Inputs:

```text
Track M*dels
Knowledge Registry
Corner Reg*ons
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

*--

# YouTube Knowledge*Pipeline

### src/youtube/segment_*urn_ranges.py

```*ext
Transcripts
    ↓
Turn Segment*
```

Output*

```text
research/youtube/turn_ra*ges.csv
```

*--

### src/youtube/extract_turn_f*cts_v2.py

```text
*urn Segments
    ↓
Structured Fact*
```

Output:

```text*research/youtube/turn_facts_v2.csv*```

*--

### src/youtube/build_track_tu*n_consensus.py

```text
Turn Facts*    ↓
Corner*Consensus
```

Provides:

```text
*orner Coaching Knowledge
Community*Techniques
Corner Characteristics
*``

---

### src/youtube/build_tra*k_fact_summary.py

```text
Turn Fa*ts
    ↓
Track Summary
```

Provid*s:

```text*Track Themes
Driving Characteristi*s
Common Coaching Advice
```

---
*# Platform Infrastructure

### src*p*pelines/build_track_catalog.py

Ou*put:

```text
generated/track_cata*og.json
```

Provides:

```text
Tr*ck Discovery
Track Layout*Metadata
*rack Asset Coverage
```

*--

### src/pipelines/build_acquis*tion_registry.py

Output:

```text*generated/acquisition_registry.jso*
```

Provides:

```text
Knowledge*Acquisition Status
Coverage Tracki*g
```

---

# Core Data Flow

```t*xt*Racing Track Maps Vector SVGs
    *           ↓

s*eleton_generator.py
              * ↓

centreline_extractor.py
      *         ↓

build_axis_library.py
*               ↓

Axis Library
   *            ↓

curvature_analyzer.*y
                ↓

build_corner_*andidate_library.py
              * ↓

build_corner_apex_library.py
 *              ↓

build_corner_regi*n_library.py
                ↓

ge*erated/corner_regions/*.json
     *          ↓

build_knowledge_regis*ry.py
                ↓

knowledge*registry.json
                ↓

b*ild_track_knowledge_pack.py
      *         ↓

knowledge_packs/*.json*

Lovely Racing
        ↓

build_e*riched_tracks.py
        ↓

Named *orners
Corner Metadata
Track Metad*ta


YouTube Transcripts
        ↓*
segment_turn_ranges.py
        ↓
*extract_turn_facts_v2.py
        ↓*
build_track*turn_consensus.py
build_track*fact_summary.py
*       ↓

Track Knowledge
Corner K*owledge
        ↓

knowledge_packs**.json
```
*