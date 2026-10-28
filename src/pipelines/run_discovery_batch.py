"""Kept for the old command: runs run_guide_discovery (same arguments, e.g. --limit 25)."""
import subprocess
import sys

raise SystemExit(subprocess.call([sys.executable, "-m", "src.pipelines.run_guide_discovery", *sys.argv[1:]]))
