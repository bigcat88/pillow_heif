from os import getenv, path
from subprocess import DEVNULL, PIPE, run
from sys import platform

from cffi import FFI

from libheif import build_libs

ffi = FFI()
with open("libheif/heif.h", "r", encoding="utf-8") as f:
    ffi.cdef(f.read())

include_dirs = ["/usr/local/include", "/usr/include"]
library_dirs = ["/usr/local/lib", "/usr/lib", "/lib"]

include_path_prefix = ""
insert = False
if platform.lower() == "darwin":
    include_path_prefix = getenv("HOMEBREW_PREFIX")
    if not include_path_prefix:
        _result = run(["brew", "--prefix"], stderr=DEVNULL, stdout=PIPE, check=False)
        if not _result.returncode and _result.stdout is not None:
            include_path_prefix = _result.stdout.decode("utf-8").rstrip("\n")
    if not include_path_prefix:
        include_path_prefix = "/opt/local"
elif platform.lower() == "win32":
    include_path_prefix = getenv("VCPKG_PREFIX")
else:
    include_path_prefix = build_libs.build_libs_linux()

if include_path_prefix:
    include_path_prefix_include = path.join(include_path_prefix, "include")
    if include_path_prefix_include not in include_dirs:
        include_dirs.append(include_path_prefix_include)
    include_path_prefix_lib = path.join(include_path_prefix, "lib")
    if include_path_prefix_lib not in library_dirs:
        library_dirs.append(include_path_prefix_lib)

if platform.lower() in ("darwin", "win32"):
    include_dirs.append(path.dirname(path.dirname(path.abspath(__file__))))

ffi.set_source(
    "_pillow_heif_cffi",
    """
     #include "libheif/heif.h"
    """,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=["heif"],
    extra_compile_args=["/d2FH4-"] if platform.lower() == "win32" else [],
)

if __name__ == "__main__":
    ffi.compile(verbose=True)
