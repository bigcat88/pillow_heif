#!/usr/bin/env python
from os import environ
from subprocess import run
from sys import executable, stderr
from traceback import format_exc

# From project folder run: `python3 .github/wheels_m1.py`
if __name__ == "__main__":
    try:
        run("brew uninstall libheif".split(), check=False)
        run("brew install --formula ./libheif/macos/libheif.rb".split(), check=True)
        print("Installing cibuildwheel...")
        args = [executable]
        args += "-m pip install -U cibuildwheel".split()
        run(args, check=True)
        print("Start building...")
        modified_env = dict(environ)
        modified_env["CIBW_SKIP"] = "pp* cp36-* cp37-* cp311-*"
        modified_env["CIBW_BUILD"] = "*-macosx_arm64"
        modified_env["CIBW_ARCHS"] = "arm64"
        modified_env["CIBW_PLATFORM"] = "macos"
        modified_env["CIBW_ENVIRONMENT"] = "MACOSX_DEPLOYMENT_TARGET=12.0"
        args = [executable]
        args += "-m cibuildwheel --platform macos --output-dir wheelhouse".split()
        run(args, env=modified_env, check=True)
        print("Build Ok.")
    except Exception as e:
        print(f"Exception: {repr(e)} ", file=stderr)
        print(format_exc())
