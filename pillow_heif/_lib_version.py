from _heif import ffi, lib  # pylint: disable=import-error


def libheif_version():
    return ffi.string(lib.heif_get_version()).decode()
