import json

vehicles = json.load(
    open(
        "generated/iracing_vehicle_index.json",
        encoding="utf-8"
    )
)

aliases = {}

for vehicle in vehicles:

    name = (
        vehicle.get(
            "carName"
        ) or ""
    )

    car_class = (
        vehicle.get(
            "carClass"
        ) or ""
    )

    aliases[
        car_class.lower()
    ] = sorted(
        set(
            [
                car_class.lower(),
                name.lower()
            ]
        )
    )

with open(
    "generated/vehicle_alias_candidates.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        aliases,
        fp,
        indent=2
    )

print(
        "classes:",
        len(aliases)
)
