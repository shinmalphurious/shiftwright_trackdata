# Repository Audit Commands

## 1. Pipeline Inventory

Get-ChildItem src\pipelines *.py |
Sort-Object Name |
Select-Object Name

## 2. Shared Modules

Get-ChildItem src\shared *.py |
Select-Object Name

## 3. Youtube Modules

Get-ChildItem src\youtube -Recurse *.py |
ForEach-Object {
    $_.FullName.Replace(
        (Get-Location).Path + "\",
        ""
    )
}

## 4. Generated Artifacts

Get-ChildItem generated |
Select-Object Name

## 5. Transcript Related Files

Get-ChildItem src\pipelines |
Where-Object {
    $_.Name -match
    "transcript|caption"
} |
Select-Object Name

## 6. Historical Transcript Files

Get-ChildItem research\youtube\transcripts |
Measure-Object

Get-ChildItem research\youtube\transcripts |
Select-Object -First 50 Name

## 7. Recently Modified Pipeline Files

Get-ChildItem src\pipelines *.py |
Sort-Object LastWriteTime -Descending |
Select-Object LastWriteTime,Name -First 100

## 8. Full Source Tree

tree src /f

## 9. Full Generated Tree

tree generated /f

## 10. Existing Architecture Files

Get-ChildItem -Recurse |
Where-Object {
    $_.Name -match
    "architecture|archtecture|readme"
} |
Select-Object FullName

## 11. Current Transcript Queue Stats

python -c "
import json

q=json.load(
    open(
        'generated/transcript_queue.json',
        encoding='utf-8'
    )
)

from collections import Counter

print(
    Counter(
        x['status']
        for x in q
    )
)
"

## 12. Discovery Catalog Stats

python -c "
import json

data=json.load(
    open(
        'generated/discovery_effectiveness.json',
        encoding='utf-8'
    )
)

print(
    'tracks',
    len(data)
)

print(
    'with guides',
    sum(
        1
        for x in data
        if x['guides']>0
    )
)

print(
    'without guides',
    sum(
        1
        for x in data
        if x['guides']==0
    )
)
"

## 13. Duplicate Pipeline Detection

Get-ChildItem src\pipelines *.py |
Select-Object Name,Length |
Sort-Object Length

## 14. Transcript Pipeline Files

Get-Content src\pipelines\claim_next_transcript.py

Get-Content src\pipelines\run_transcript_pipeline.py

Get-Content src\pipelines\attempt_transcript_download.py

Get-Content src\shared\transcript_backoff.py

## 15. Guide Catalog Summary

python -m src.pipelines.report_catalog_summary
