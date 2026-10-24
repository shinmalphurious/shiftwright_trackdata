from pathlib import Path

consensus_dir = Path(
    "generated/turn_consensus"
)

files = list(
    consensus_dir.glob("*.json")
)

for file in files:
    file.unlink()

print(
    "removed:",
    len(files)
)
