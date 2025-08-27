#!/usr/bin/env python3
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "scripts/cli.py", "run-scheduler"])