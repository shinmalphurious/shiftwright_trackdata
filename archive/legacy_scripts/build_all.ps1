[cmdletbinding()]
param()

python -m src.pipelines.build_axis_library

python -m src.pipelines.normalize_axis_library

python -m src.pipelines.build_axis_registry

python -m src.pipelines.build_corner_apex_library

python -m src.pipelines.build_corner_region_library

python -m src.pipelines.build_corner_metrics_library

python -m src.pipelines.build_corner_characteristics_library

python -m src.pipelines.build_corner_classification_library
