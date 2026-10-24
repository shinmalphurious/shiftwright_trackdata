import json

selection = json.load(
    open(
        "generated/discovery_selection.json",
        encoding="utf-8"
    )
)

catalog_entry = {
    "track_id":
        selection["track_id"],

    "layout":
        selection["layout"],

    "captions_available":
        True,

    "selected_guides":
        selection["selected_guides"]
}

with open(
    f"generated/guide_catalog/{selection['track_id']}.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        catalog_entry,
        fp,
        indent=2
    )

print(
        "updated"
)
