"""Run the offline example and both table checks, stopping at the first error."""

from pathlib import Path
import shutil
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent
    node = shutil.which("node")
    if node is None:
        sys.exit("Install Node.js 18 or later and make node available on PATH.")

    commands = (
        (node, "scripts/replay.mjs"),
        (node, "scripts/table3.mjs"),
        (sys.executable, "scripts/table5.py"),
    )
    for executable, script in commands:
        print(f"\n== {script} ==", flush=True)
        result = subprocess.run([executable, script], cwd=root)
        if result.returncode != 0:
            sys.exit(result.returncode)
    print("\nAll three checks passed.")


if __name__ == "__main__":
    main()
