#!/usr/bin/env python
from os import chdir, environ, path
from subprocess import run
from sys import executable, stderr
from traceback import format_exc

if __name__ == "__main__":
    try:
        chdir(path.dirname(path.abspath(__file__)))
        print("Installing cibuildwheel...")
        args = [executable]
        args += "-m pip install cibuildwheel".split()
        run(args, check=True)
        print("Start building...")
        modified_env = dict(environ)
        modified_env["CIBW_SKIP"] = "pp* cp36-* cp37-* cp38-*"
        modified_env["CIBW_BUILD"] = "*-macosx_arm64"
        modified_env["CIBW_ARCHS"] = "arm64"
        modified_env["CIBW_PLATFORM"] = "macos"
        modified_env["CIBW_ENVIRONMENT"] = "MACOSX_DEPLOYMENT_TARGET=12.0"
        # Temporary workaround, will look at this after war ends.
        modified_env["CIBW_BEFORE_ALL"] = "HOMEBREW_PREFIX=$(brew --prefix) && REPAIR_LIBRARY_PATH=$HOMEBREW_PREFIX/lib"
        args = [executable]
        args += "-m cibuildwheel --platform macos --output-dir wheelhouse".split()
        run(args, env=modified_env, check=True)
        print("Build Ok.")
    except Exception as e:
        print(f"Exception: {repr(e)} ", file=stderr)
        print(format_exc())
