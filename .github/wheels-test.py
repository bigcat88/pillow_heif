"""Runs tests against a built wheel from cibuildwheel, optionally collecting coverage."""

import os
import shutil
import subprocess
import sys

PROJECT = sys.argv[1]
TESTS = os.path.join(PROJECT, "tests")
COVERAGE_OUT = os.environ.get("COVERAGE_OUT")

if COVERAGE_OUT and sys.implementation.name == "cpython":
    if sys.version_info >= (3, 12):
        os.environ.setdefault("COVERAGE_CORE", "sysmon")
    rcfile = os.path.join(PROJECT, "pyproject.toml")
    cmd = [sys.executable, "-m", "coverage", "run", f"--rcfile={rcfile}", "-m", "pytest", TESTS]
    subprocess.run(cmd, check=True)
    os.makedirs(COVERAGE_OUT, exist_ok=True)
    data_file = f".coverage.{os.environ['CIBUILDWHEEL_BUILD_IDENTIFIER']}"
    shutil.move(".coverage", os.path.join(COVERAGE_OUT, data_file))
else:
    subprocess.run([sys.executable, "-m", "pytest", TESTS], check=True)
