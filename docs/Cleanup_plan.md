# Track Knowledge Repository Cleanup Plan

## Purpose

This document defines the cleanup and stabilization plan for the Track Knowledge Repository.

The objective is to transition the project from a collection of experimental pipelines into a deterministic knowledge generation system capable of producing a standardized knowledge pack for every track layout.

The final target architecture is:

```text
Track Discovery
        ↓
Geometry Extraction
        ↓
Corner Modelling
        ↓
Knowledge Registry
        ↓
Knowledge Enrichment
        ↓
Knowledge Packs
        ↓
LLM Interpretation
```

The focus of this cleanup is architectural stability before expanding acquisition efforts.

---

# Phase 1 - Architecture Freeze

## Objective

Establish a single source of truth for the production pipeline.

Before deleting, refactoring, or adding functionality, formally define the approved execution path.

## Deliverables

### Create

```text
docs/
    architecture.md
```

### Approved Production Pipeline

```text
build_track_catalog

build_axis_library
normalize_axis_library
build_axis_registry

build_corner_candidate_library
build_corner_apex_library
build_corner_region_library

build_corner_metrics_library
build_corner_characteristics_library
build_corner_dependency_library

build_enriched_tracks

build_knowledge_registry

build_track_knowledge_pack
```

### Approved Enrichment Pipeline

```text
segment_turn_ranges
extract_turn_facts_v2

build_track_turn_consensus
build_track_fact_summary
```

## Exit Criteria

- Official architecture documented
- Core execution path agreed
- No ambiguity about production pipeline

---

# Phase 2 - File Classification

## Objective

Determine the status of every Python file in the repository.

Every file must belong to one category.

## Categories

### CORE

Required for production execution.

Examples:

```text
build_axis_library.py
build_corner_region_library.py
build_knowledge_registry.py
build_track_knowledge_pack.py
```

### SUPPORT

Diagnostics, validation and audit utilities.

Examples:

```text
audit_corner_sources.py
audit_corner_distribution.py
report_acquisition_status.py
```

### EXPERIMENTAL

Old prototypes, abandoned approaches and temporary scripts.

Examples:

```text
legacy extraction attempts
one-off migration scripts
temporary debugging utilities
```

## Exit Criteria

- Every file classified
- No unknown ownership
- Candidates for removal identified

---

# Phase 3 - Repository Separation

## Objective

Separate production code from research work.

Current responsibilities are mixed together.

## Target Structure

```text
src/
    production code

research/
    acquisition experiments
    investigations
    notebooks

generated/
    generated artifacts

docs/
    architecture
    planning
```

## Rules

### Production Rule

```text
src imports src
```

### Research Rule

```text
research imports src

src never imports research
```

### Generated Rule

```text
generated contains outputs only
```

No source code should exist inside generated.

## Exit Criteria

- Clean directory ownership
- Production and research separated
- Generated folder standardized

---

# Phase 4 - Geometry Pipeline Stabilization

## Objective

Lock the geometry pipeline as stable infrastructure.

Current coverage:

```text
Tracks: 424
Axis Models: 424
Corner Regions: 424
```

Geometry is no longer the bottleneck.

## Scope

```text
skeleton_generator.py

centreline_extractor.py

build_axis_library.py
normalize_axis_library.py
build_axis_registry.py

curvature_peak_detector.py

build_corner_candidate_library.py
build_corner_apex_library.py
build_corner_region_library.py
```

## Actions

### Validate

- Axis generation coverage
- Centreline quality
- Corner discovery coverage

### Freeze

No major redesigns unless critical defects are found.

## Exit Criteria

- Geometry pipeline considered production stable

---

# Phase 5 - Generated Artifact Reorganization

## Objective

Create a predictable output structure.

## Target Layout

```text
generated/

catalog/

geometry/
    axes/
    normalized_axes/
    axis_registry/

corners/
    candidates/
    apexes/
    regions/
    metrics/
    characteristics/
    dependencies/

youtube/
    summaries/
    consensus/

knowledge/
    registry/

knowledge_packs/
```

## Benefits

### Easier navigation

Artifacts grouped by responsibility.

### Easier audits

Pipeline outputs become easier to verify.

### Easier automation

Future orchestration becomes simpler.

## Exit Criteria

- Generated outputs reorganized
- Paths standardized

---

# Phase 6 - Remove Console-Based Pipelines

## Objective

All pipelines should create structured assets instead of console output.

## Convert

### Current

```text
segment_turn_ranges.py
extract_turn_facts_v2.py
build_track_turn_consensus.py
build_track_fact_summary.py
```

### Problem

Much of the information currently exists only as text printed to the terminal.

### Target

Every stage writes machine-readable artifacts.

Example:

```text
generated/youtube/
```

### Output Formats

```json
summary.json
```

```json
consensus.json
```

```json
evidence.json
```

## Exit Criteria

- No critical information exists only in console output
- Artifacts become reusable

---

# Phase 7 - YouTube Knowledge Normalization

## Objective

Convert YouTube extraction from keyword collection into structured knowledge.

## Current State

```json
{
  "fact": "slippery"
}
```

## Target State

```json
{
  "fact": "slippery",
  "occurrences": 4,
  "evidence": [
    "This corner is incredibly slippery.",
    "Very slippy on exit."
  ]
}
```

## Required Outputs

### Track Summary

```json
{
  "track_id": 485,
  "facts": [],
  "evidence": []
}
```

### Turn Consensus

```json
{
  "track_id": 485,
  "turns": []
}
```

## Exit Criteria

- Evidence preserved
- Fact confidence measurable
- Knowledge reusable by LLM systems

---

# Phase 8 - Knowledge Pack Integration

## Objective

Make knowledge packs the canonical destination for all enrichment.

## Current State

```json
{
  "youtube_summary": {},
  "turn_consensus": {}
}
```

## Required Integration

Create:

```text
build_youtube_knowledge_library.py
```

Pipeline:

```text
Track Fact Summary
        +
Turn Consensus
        ↓
YouTube Knowledge
        ↓
Knowledge Pack
```

## Target

Every knowledge pack automatically receives available YouTube enrichment.

## Exit Criteria

- No disconnected enrichment artifacts
- Knowledge packs become authoritative

---

# Phase 9 - Knowledge Pack Schema Freeze

## Objective

Define and lock the long-term schema.

## Canonical Structure

```json
{
  "track_id": 485,

  "knowledge_level": "direct",

  "metadata": {},

  "named_corners": [],

  "generated_corner_regions": [],

  "corner_characteristics": [],

  "corner_dependencies": [],

  "youtube_summary": {},

  "turn_consensus": {},

  "evidence": []
}
```

## Rules

### New Data Sources

Must extend the schema.

### New Artifacts

Should not create alternative storage models.

Knowledge packs remain the single source of truth.

## Exit Criteria

- Schema documented
- No competing models

---

# Phase 10 - Source Adapter Architecture

## Objective

Standardize all enrichment systems.

Future sources:

```text
Lovely

YouTube

Garage61

Telemetry

Car Datasheets
```

## Adapter Contract

Every source should produce:

```json
{
  "track_id": 485,
  "facts": [],
  "evidence": []
}
```

## Design Principle

```text
Adapters do not talk to each other.
```

```text
Knowledge packs consume adapters.
```

This prevents coupling between acquisition systems.

## Exit Criteria

- Unified enrichment architecture
- Predictable integrations

---

# Phase 11 - Repository Purge

## Objective

Remove obsolete code.

## Remove

```text
Dead experiments

Abandoned prototypes

Legacy extraction attempts

Temporary debugging utilities

One-off migration scripts
```

## Keep

```text
Production pipelines

Diagnostic utilities

Architectural documentation
```

## Deletion Rule

A file must answer:

```text
What creates it?
```

and

```text
What consumes it?
```

If neither answer exists, the file is a deletion candidate.

## Exit Criteria

- No orphaned code
- Minimal maintenance burden

---

# Final Target State

```text
TRACK DISCOVERY
        ↓
GEOMETRY EXTRACTION
        ↓
CORNER MODELLING
        ↓
KNOWLEDGE REGISTRY
        ↓
KNOWLEDGE ADAPTERS
        ↓
KNOWLEDGE PACKS
        ↓
LLM ANALYSIS
```

---

# Priority Order

## Mandatory Cleanup

```text
Phase 1
Phase 2
Phase 3
```

## Architecture Hardening

```text
Phase 4
Phase 5
Phase 6
Phase 7
Phase 8
```

## Productionisation

```text
Phase 9
Phase 10
Phase 11
```

---

# Immediate Next Action

Begin with **Phase 2 (File Classification).**

Before any new development:

```text
Inventory every Python file
        ↓
Classify:
    CORE
    SUPPORT
    EXPERIMENTAL
        ↓
Identify deletion candidates
```

This will provide a complete view of the actual production footprint before further refactoring or acquisition work begins.