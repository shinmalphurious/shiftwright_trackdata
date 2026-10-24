$files = @(

    # Geometry

    "src\geometry\skeleton_generator.py",
    "src\geometry\centreline_extractor.py",

    # Corner Detection

    "src\corners\curvature_peak_detector.py",
    "src\corners\corner_region_detector.py",
    "src\corners\region_deduplicator.py",

    # Corner Classification

    "src\corners\characteristics.py",
    "src\corners\corner_dependency.py",
    "src\corners\track_insights.py",

    # Geometry Build

    "src\pipelines\build_axis_library.py",
    "src\pipelines\normalize_axis_library.py",
    "src\pipelines\build_axis_registry.py",

    # Corner Generation

    "src\pipelines\build_corner_candidate_library.py",
    "src\pipelines\build_corner_apex_library.py",
    "src\pipelines\build_corner_region_library.py",

    # Corner Enrichment

    "src\pipelines\build_corner_metrics_library.py",
    "src\pipelines\build_corner_characteristics_library.py",
    "src\pipelines\build_corner_dependency_library.py",
    "src\pipelines\build_enriched_tracks.py",

    # Knowledge Layer

    "src\models\track_knowledge.py",
    "src\pipelines\build_knowledge_registry.py",
    "src\pipelines\build_track_knowledge_pack.py",

    # Discovery / Catalog

    "src\pipelines\build_track_catalog.py",
    "src\pipelines\build_acquisition_registry.py",

    # YouTube Knowledge

    "src\youtube\segment_turn_ranges.py",
    "src\youtube\extract_turn_facts_v2.py",
    "src\youtube\build_track_turn_consensus.py",
    "src\youtube\build_track_fact_summary.py"
)

$out = "core_pipeline_dump.txt"

$writer = [System.IO.StreamWriter]::new(
    $out,
    $false,
    [System.Text.Encoding]::UTF8
)

foreach ($file in $files)
{
    if (Test-Path $file)
    {
        $writer.WriteLine("")
        $writer.WriteLine("=" * 100)
        $writer.WriteLine("FILE: $file")
        $writer.WriteLine("=" * 100)
        $writer.WriteLine("")

        Get-Content $file | ForEach-Object {
            $writer.WriteLine($_)
        }
    }
}

$writer.Close()

Write-Host ""
Write-Host "Created:" $out
