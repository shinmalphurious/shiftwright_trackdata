import subprocess

print()
print("CLAIM")

subprocess.run(
    [
        "python",
        "-m",
        "src.pipelines.claim_next_track"
    ]
)

print()
print("SEARCH PAYLOAD")

subprocess.run(
    [
        "python",
        "-m",
        "src.pipelines.build_search_payload"
    ]
)

print()
print("DISCOVERY TASK")

subprocess.run(
    [
        "python",
        "-m",
        "src.pipelines.build_discovery_task"
    ]
)

print()
print("DISCOVERY")

subprocess.run(
    [
        "python",
        "-m",
        "src.pipelines.run_discovery_provider"
    ]
)

print()
print("SELECTION")

subprocess.run(
    [
        "python",
        "-m",
        "src.pipelines.select_best_guides"
    ]
)
