import json
from pathlib import Path

# TODO:
# Replace with actual source from main project

SOURCE = Path(
    "../Project_Shiftwright/generated"
)

for file in SOURCE.glob("*.json"):

    print(file.name)
