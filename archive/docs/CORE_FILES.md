# CORE FILES

This document defines the only files required to rebuild the Track Knowledge Repository.

Source of truth:

core_pipeline_dump.txt

Any file not listed here is considered rebuildable and should not be preserved unless later promoted into the architecture.

---

# Geometry

src\geometry\skeleton_generator.py

src\geometry\centreline_extractor.py

src\geometry\curvature_analyzer.py

---

# Corner Logic

src\corners\curvature_peak_detector.py

src\corners\corner_region_detector.py

src\corners\region_deduplicator.py

src\corners\characteristics.py

src\corners\corner_dependency.py

src\corners\track_insights.py

---

# Models

src\models\track_knowledge.py

---

# Core Pipeline

src\pipelines\build_track_catalog.py

src\pipelines\build_acquisition_registry.py

src\pipelines\build_axis_library.py

src\pipelines\normalize_axis_library.py

src\pipelines\build_axis_registry.py

src\pipelines\build_corner_candidate_library.py

src\pipelines\build_corner_apex_library.py

src\pipelines\build_corner_region_library.py

src\pipelines\build_corner_metrics_library.py

src\pipelines\build_corner_characteristics_library.py

src\pipelines\build_corner_dependency_library.py

src\pipelines\build_enriched_tracks.py

src\pipelines\build_knowledge_registry.py

src\pipelines\build_track_knowledge_pack.py

---

# YouTube Pipeline

src\youtube\segment_turn_ranges.py

src\youtube\extract_turn_facts_v2.py

src\youtube\build_track_turn_consensus.py

src\youtube\build_track_fact_summary.py

---

# Core Data Flow

Track SVGs
    ?
skeleton_generator.py
    ?
centreline_extractor.py
    ?
build_axis_library.py
    ?
normalize_axis_library.py
    ?
build_axis_registry.py
    ?
build_corner_candidate_library.py
    ?
build_corner_apex_library.py
    ?
build_corner_region_library.py
    ?
build_corner_metrics_library.py
    ?
build_corner_characteristics_library.py
    ?
build_corner_dependency_library.py
    ?
build_enriched_tracks.py
    ?
build_knowledge_registry.py
    ?
build_track_knowledge_pack.py

YouTube Transcripts
    ?
segment_turn_ranges.py
    ?
extract_turn_facts_v2.py
    ?
build_track_turn_consensus.py
build_track_fact_summary.py
    ?
Knowledge Pack Enrichment

# Package Files

src\__init__.py

src\geometry\__init__.py

src\corners\__init__.py

src\pipelines\__init__.py
