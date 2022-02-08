from _heif import ffi, lib


def libheif_version():
    return ffi.string(lib.heif_get_version()).decode()
