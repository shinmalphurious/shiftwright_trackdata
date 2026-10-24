import json
from pathlib import Path

SOURCE = Path(
    "external/lovely-car-data/data/iracing"
)

cars = []

for file in sorted(
    SOURCE.glob("*.json")
):

    try:

        data = json.load(
            open(
                file,
                encoding="utf-8"
            )
        )

    except Exception:

        continue

    cars.append(
        {
            "id":
                file.stem,

            "carName":
                data.get(
                    "carName"
                ),

            "carClass":
                data.get(
                    "carClass"
                )
        }
    )

with open(
    "generated/iracing_vehicle_index.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        cars,
        fp,
        indent=2
    )

print(
        "vehicles:",
        len(cars)
)
