"""Run every step after transcripts are downloaded, in order, then import into Shiftwright.

    python -m src.pipelines.run_post_download
    python -m src.pipelines.run_post_download --skip-research --no-import

A failed step does not stop the run: the next steps still run (on whatever output the
earlier steps left). At the end a report is written to
generated/post_download_runs/<timestamp>/ with:
    report.md    what passed, what failed, and the last lines of each failure
    report.json  the same, for scripts
    logs/        the full output of every step
Ctrl+C stops the run and still writes the report.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PYTHON = sys.executable
DEFAULT_SHIFTWRIGHT = Path(r"E:\Project_Shiftwright")
RUNS_DIR = Path("generated/post_download_runs")
TAIL_LINES = 40


def build_steps(args):
    extract = ["extract_corner_guidance"]
    if args.include_likely:
        extract.append("--include-likely")
    if args.model:
        extract += ["--model", args.model]

    research = ["research_track_candidates", "--all"]
    if args.no_ai:
        research.append("--no-ai")
    if args.model:
        research += ["--model", args.model]

    steps = [
        ("verify", "Verify lap-guide transcripts", ["verify_lap_guide_transcripts"]),
        ("extract", "Extract corner guidance (Ollama)", extract),
        ("enrich", "Assign notes to corners", ["enrich_corner_assignments"]),
        ("coverage", "Telemetry coverage", ["build_telemetry_coverage"]),
        ("validate", "Validate track knowledge", ["validate_track_knowledge"]),
    ]
    if not args.skip_research:
        steps += [
            ("research", "Research corner facts", research),
            ("validate_facts", "Validate corner facts", ["validate_knowledge_candidates"]),
        ]
    steps += [
        ("corner_guidance", "Build corner guidance", ["build_corner_guidance"]),
        ("knowledge_pack", "Build track knowledge packs", ["build_track_knowledge_pack"]),
    ]
    return [
        {"key": key, "name": name, "command": [PYTHON, "-m", "src.pipelines." + cmd[0], *cmd[1:]], "cwd": None}
        for key, name, cmd in steps
    ]


def import_step(shiftwright: Path):
    python = shiftwright / ".venv" / "Scripts" / "python.exe"
    if not python.exists():
        python = Path(PYTHON)
    return {"key": "import", "name": "Import packs into Shiftwright",
            "command": [str(python), "scripts/import_knowledge_packs.py"], "cwd": str(shiftwright)}


def run_step(step, log_path: Path):
    """Run one step, echoing its output live and saving it to log_path. Returns (exit code, tail)."""
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    tail = []
    with open(log_path, "w", encoding="utf-8") as log:
        log.write(" ".join(step["command"]) + "\n\n")
        try:
            process = subprocess.Popen(step["command"], cwd=step["cwd"], env=env,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, encoding="utf-8", errors="replace", bufsize=1)
        except OSError as error:
            message = f"Could not start step: {error}"
            print(message)
            log.write(message + "\n")
            return -1, [message]
        try:
            for line in process.stdout:
                sys.stdout.write(line)
                log.write(line)
                tail.append(line.rstrip("\n"))
                if len(tail) > TAIL_LINES:
                    tail.pop(0)
            return process.wait(), tail
        except KeyboardInterrupt:
            process.kill()
            process.wait()
            raise


def write_report(run_dir: Path, results, started_at: datetime, total_seconds: float, interrupted: bool):
    failed = [r for r in results if r["status"] == "failed"]
    data = {
        "started": started_at.isoformat(timespec="seconds"),
        "minutes": round(total_seconds / 60, 1),
        "interrupted": interrupted,
        "passed": sum(r["status"] == "passed" for r in results),
        "failed": len(failed),
        "not_run": sum(r["status"] == "not_run" for r in results),
        "steps": results,
    }
    (run_dir / "report.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    lines = [
        f"# Post-download run {started_at:%Y-%m-%d %H:%M}",
        "",
        f"{data['passed']} passed, {data['failed']} failed, {data['not_run']} not run"
        f" - {data['minutes']} min" + (" - **stopped with Ctrl+C**" if interrupted else ""),
        "",
        "| # | Step | Result | Time | Log |",
        "|---|------|--------|------|-----|",
    ]
    for index, r in enumerate(results, 1):
        result = {"passed": "passed", "failed": f"**FAILED** (exit {r['exit_code']})", "not_run": "not run"}[r["status"]]
        took = f"{r['seconds']:.0f}s" if r["seconds"] is not None else ""
        log = f"[log]({r['log']})" if r["log"] else ""
        lines.append(f"| {index} | {r['name']} | {result} | {took} | {log} |")

    if failed:
        lines += ["", "## Failures", ""]
        first = failed[0]
        lines += [f"Fix the first failure first: later steps use its output, so they may have failed "
                  f"or run on stale data because of it. First failure: **{first['name']}**.", ""]
        for r in failed:
            lines += [f"### {r['name']}", "", f"`{' '.join(r['command'])}`", "",
                      f"Last {len(r['tail'])} lines (full output in `{r['log']}`):", "", "```text",
                      *r["tail"], "```", ""]
        lines += ["Re-run one step on its own with the command above, or the whole run with",
                  "`python -m src.pipelines.run_post_download`; finished work is kept."]
    else:
        lines += ["", "No failures." if not interrupted else ""]

    (run_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-research", action="store_true", help="skip the corner-fact research and validation steps")
    parser.add_argument("--no-ai", action="store_true", help="research with geometry rules only, no Ollama")
    parser.add_argument("--include-likely", action="store_true", help="also extract from likely (not only confirmed) walkthroughs")
    parser.add_argument("--model", help="Ollama model for extraction and research")
    parser.add_argument("--no-import", action="store_true", help="don't import the packs into Shiftwright")
    parser.add_argument("--shiftwright", type=Path, default=DEFAULT_SHIFTWRIGHT, help="Project_Shiftwright folder")
    args = parser.parse_args()

    steps = build_steps(args)
    if not args.no_import:
        steps.append(import_step(args.shiftwright))

    started_at = datetime.now()
    run_dir = RUNS_DIR / started_at.strftime("%Y-%m-%d_%H-%M-%S")
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)

    results = [{"key": s["key"], "name": s["name"], "command": s["command"], "status": "not_run",
                "exit_code": None, "seconds": None, "log": None, "tail": []} for s in steps]
    started = time.time()
    interrupted = False
    try:
        for index, (step, result) in enumerate(zip(steps, results), 1):
            print(f"\n{'=' * 80}\n[{index}/{len(steps)}] {step['name']}\n"
                  f"{' '.join(step['command'])}\n{'=' * 80}", flush=True)
            log_path = run_dir / "logs" / f"{index:02d}_{step['key']}.log"
            step_start = time.time()
            exit_code, tail = run_step(step, log_path)
            result.update(exit_code=exit_code, seconds=round(time.time() - step_start, 1),
                          log=f"logs/{log_path.name}", status="passed" if exit_code == 0 else "failed",
                          tail=tail if exit_code != 0 else [])
            if exit_code == 0:
                print(f"-> done in {result['seconds']:.0f}s", flush=True)
            else:
                print(f"-> FAILED (exit {exit_code}) after {result['seconds']:.0f}s - continuing", flush=True)
    except KeyboardInterrupt:
        interrupted = True
        print("\nStopped with Ctrl+C - writing report.")

    write_report(run_dir, results, started_at, time.time() - started, interrupted)

    failed = [r["name"] for r in results if r["status"] == "failed"]
    print(f"\n{'=' * 80}")
    print(f"Finished: {sum(r['status'] == 'passed' for r in results)} passed, {len(failed)} failed.")
    for name in failed:
        print(f"  FAILED: {name}")
    print(f"Report: {(run_dir / 'report.md').resolve()}")
    sys.exit(1 if failed or interrupted else 0)


if __name__ == "__main__":
    main()
