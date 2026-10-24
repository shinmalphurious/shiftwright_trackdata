import json
from pathlib import Path

generated = Path("generated")

files = sorted(
    int(f.stem)
    for f in generated.glob("*.json")
)

print()
print(f"Generated files: {len(files)}")
print()

print("First 25:")
for x in files[:25]:
    print(x)

print()
print("Last 25:")
for x in files[-25:]:
    print(x)
