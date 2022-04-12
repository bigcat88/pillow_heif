"""
Undocumented private functions for other code to look better.
"""
from _pillow_heif_cffi import ffi


def copy_image_data(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    if dest_stride == source_stride:
        ffi.memmove(dest_data, src_data, len(src_data))
    else:
        p_source = ffi.from_buffer("uint8_t*", src_data)
        for i in range(height):
            ffi.memmove(dest_data + dest_stride * i, p_source + source_stride * i, source_stride)


def get_stride(bit_depth: int, mode: str, width: int, **kwargs) -> int:
    __stride = kwargs.get("stride", None)
    __factor = 1 if bit_depth == 8 else 2
    return __stride if __stride else width * 3 * __factor if mode == "RGB" else width * 4 * __factor


def heif_ctx_as_dict(bit_depth: int, mode: str, size: tuple, data, **kwargs) -> dict:
    return {
        "bit_depth": bit_depth,
        "mode": mode,
        "size": size,
        "data": data,
        "stride": get_stride(bit_depth, mode, size[0], **kwargs),
        "additional_info": kwargs.get("add_info", {}),
    }
