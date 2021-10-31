import os
from cffi import FFI

ffibuilder = FFI()


with open("libheif/heif.h", "r", encoding="utf-8") as f:
    ffibuilder.cdef(f.read())


include_dirs = ["/usr/local/include", "/usr/include", "/opt/local/include"]
library_dirs = ["/usr/local/lib", "/usr/lib", "/lib", "/opt/local/lib"]
homebrew_prefix = os.getenv("HOMEBREW_PREFIX")
if homebrew_prefix:
    include_dirs.append(os.path.join(homebrew_prefix, "include"))
    library_dirs.append(os.path.join(homebrew_prefix, "lib"))


ffibuilder.set_source(
    "pillow_heif._libheif",
    """
     #include "libheif/heif.h"
    """,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=["heif"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
