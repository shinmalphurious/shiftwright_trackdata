import json

vehicles = json.load(
    open(
        "generated/iracing_vehicle_index.json",
        encoding="utf-8"
    )
)

aliases = json.load(
    open(
        "data/vehicle_aliases.json",
        encoding="utf-8"
    )
)

for vehicle in vehicles:

    key = (
        vehicle.get(
            "carClass",
            ""
        )
        .lower()
    )

    vehicle[
        "aliases"
    ] = aliases.get(
        key,
        []
    )

with open(
    "generated/iracing_vehicle_index.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        vehicles,
        fp,
        indent=2
    )

print(
        "vehicles:",
        len(vehicles)
)
