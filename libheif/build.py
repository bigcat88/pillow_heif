import sys
from os import getenv, path
from pathlib import Path
from shutil import copy
from subprocess import DEVNULL, PIPE, run
from warnings import warn

from cffi import FFI

from libheif import linux_build_libs

ffi = FFI()
with open("libheif/heif.h", "r", encoding="utf-8") as f:
    ffi.cdef(f.read())

ffi.cdef(
    """
    extern "Python" int64_t callback_tell(void*);
    extern "Python" int callback_seek(int64_t, void*);
    extern "Python" int callback_read(void*, size_t, void*);
    extern "Python" struct heif_error callback_write(struct heif_context*, const void*, size_t, void*);
    extern "Python" enum heif_reader_grow_status callback_wait_for_file_size(int64_t, void*);
"""
)

with open("pillow_heif/helpers.h", "r", encoding="utf-8") as f:
    ffi.cdef(f.read())


include_dirs = ["/usr/local/include", "/usr/include"]
library_dirs = ["/usr/local/lib", "/usr/lib64", "/usr/lib", "/lib"]

include_path_prefix = ""
insert = False
if sys.platform.lower() == "darwin":
    include_path_prefix = getenv("HOMEBREW_PREFIX")
    if not include_path_prefix:
        _result = run(["brew", "--prefix"], stderr=DEVNULL, stdout=PIPE, check=False)
        if not _result.returncode and _result.stdout is not None:
            include_path_prefix = _result.stdout.decode("utf-8").rstrip("\n")
    if not include_path_prefix:
        include_path_prefix = "/opt/local"
elif sys.platform.lower() == "win32":
    include_path_prefix = getenv("MSYS2_PREFIX")
    if include_path_prefix is None:
        include_path_prefix = "C:\\msys64\\mingw64"
        warn(f"MSYS2_PREFIX environment variable is not set. Assuming `MSYS2_PREFIX={include_path_prefix}`")
else:
    include_path_prefix = linux_build_libs.build_libs()

# Need to include "lib" directory to find "heif" library.
include_path_prefix_lib = path.join(include_path_prefix, "lib")
if include_path_prefix_lib not in library_dirs:
    library_dirs.append(include_path_prefix_lib)

# MSYS2: rename "libheif.dll.a" to "libheif.lib"
if sys.platform.lower() == "win32":
    lib_export_file = Path(path.join(include_path_prefix_lib, "libheif.dll.a"))
    if lib_export_file.is_file():
        copy(lib_export_file, path.join(include_path_prefix_lib, "libheif.lib"))
    else:
        warn("If you build this with MSYS2, you should not see this warning.")

# Adds project root to `include` path
include_dirs.append(path.dirname(path.dirname(path.abspath(__file__))))

ffi.set_source(
    "_pillow_heif_cffi",
    r"""
    #include "libheif/heif.h"
    #include "pillow_heif/helpers.c"
    """,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=["libheif"] if sys.platform.lower() == "win32" else ["heif"],
    extra_compile_args=["/d2FH4-"] if sys.platform.lower() == "win32" else [],
)

if __name__ == "__main__":
    ffi.compile(verbose=True)
