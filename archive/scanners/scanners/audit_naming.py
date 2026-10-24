from pathlib import Path
import re
import json

ROOT = Path(
    r"E:\Project_Shiftwright\external\racing-track-maps-vector\from-iracing"
)

TRACK_PATTERN = re.compile(r"^(\d+)-(.+)$")

issues = []

for category_dir in ROOT.iterdir():

    if not category_dir.is_dir():
        continue

    category = category_dir.name

    for venue_dir in category_dir.iterdir():

        if not venue_dir.is_dir():
            continue

        venue = venue_dir.name

        for layout_dir in venue_dir.iterdir():

            if not layout_dir.is_dir():
                continue

            folder_name = layout_dir.name

            m = TRACK_PATTERN.match(folder_name)

            if not m:
                issues.append({
                    "type": "invalid_track_folder",
                    "path": str(layout_dir)
                })
                continue

            track_id = int(m.group(1))
            remainder = m.group(2)

            expected_prefix = f"{venue}-"

            if not (
                remainder == venue or
                remainder.startswith(expected_prefix)
            ):
                issues.append({
                    "type": "venue_mismatch",
                    "track_id": track_id,
                    "venue": venue,
                    "folder": folder_name,
                    "remainder": remainder
                })

            if "--" in folder_name:
                issues.append({
                    "type": "double_dash",
                    "track_id": track_id,
                    "folder": folder_name
                })

            if folder_name.endswith("-"):
                issues.append({
                    "type": "trailing_dash",
                    "track_id": track_id,
                    "folder": folder_name
                })

            if folder_name.count(str(track_id)) > 1:
                issues.append({
                    "type": "duplicate_id_string",
                    "track_id": track_id,
                    "folder": folder_name
                })

print()
print(f"Issues found: {len(issues)}")

with open(
    "registry/naming_audit.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        issues,
        f,
        indent=2
    )

for issue in issues[:50]:
    print(issue)
