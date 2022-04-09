#!/usr/bin/env python
from os import chdir, environ, path
from subprocess import PIPE, run
from sys import executable
from traceback import format_exc


def my_print(file, *arguments):
    print(*arguments, file=file, flush=True)
    print(*arguments, flush=True)


if __name__ == "__main__":
    chdir(path.dirname(path.abspath(__file__)))
    with open("output.txt", "w") as f:
        try:
            my_print(f, "Installing cibuildwheel...")
            args = [executable]
            args += "-m pip install -v -v cibuildwheel".split()
            result = run(args, check=False, stdout=PIPE, stderr=PIPE)
            my_print(f, result.stdout.decode("utf-8"))
            my_print(f, result.stderr.decode("utf-8"))
            if result.returncode != 0:
                raise Exception(f"pip install `cibuildwheel` fails. Code:{result.returncode}")
            my_print(f, "Start building...")
            modified_env = dict(environ)
            modified_env["CIBW_SKIP"] = "pp* cp36-* cp37-* cp38-*"
            modified_env["CIBW_BUILD"] = "*-macosx_arm64"
            modified_env["CIBW_ARCHS"] = "arm64"
            modified_env["CIBW_PLATFORM"] = "macos"
            modified_env["CIBW_ENVIRONMENT"] = "MACOSX_DEPLOYMENT_TARGET=12.0"
            # modified_env["CIBW_TEST_EXTRAS"] = "tests-min"
            # Temporary workaround, will look at this after war ends.
            modified_env[
                "CIBW_BEFORE_ALL"
            ] = "HOMEBREW_PREFIX=$(brew --prefix) && REPAIR_LIBRARY_PATH=$HOMEBREW_PREFIX/lib"
            args = [executable]
            args += "-m cibuildwheel --platform macos --output-dir wheelhouse".split()
            result = run(args, env=modified_env, check=False, stdout=PIPE, stderr=PIPE)
            my_print(f, result.stdout.decode("utf-8"))
            my_print(f, result.stderr.decode("utf-8"))
            if result.returncode != 0:
                raise Exception(f"Build Fails. Code:{result.returncode}")
            my_print(f, "Build Ok.")
        except Exception as e:
            my_print(f, f"Exception: {repr(e)} ")
            my_print(f, format_exc())
