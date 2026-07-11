"""Options to change pillow_heif's runtime behavior."""

DECODE_THREADS = 4
"""Maximum number of threads to use for decoding images(when it is possible)

When use pillow_heif as a plugin you can set it with: `register_*_opener(decode_threads=8)`"""


THUMBNAILS = True
"""Option to enable/disable thumbnail support

When use pillow_heif as a plugin you can set it with: `register_*_opener(thumbnails=False)`"""


DEPTH_IMAGES = True
"""Option to enable/disable depth image support

When use pillow_heif as a plugin you can set it with: `register_*_opener(depth_images=False)`"""


AUX_IMAGES = True
"""Option to enable/disable auxiliary image support

When use pillow_heif as a plugin you can set it with: `register_*_opener(aux_images=False)`"""


QUALITY = None
"""Default encoding quality

.. note:: Quality specified during calling ``save`` has higher priority then this.

Possible values: None, -1, range(0-100).
Set -1 for lossless quality or from 0 to 100, where 0 is lowest and 100 is highest.

.. note:: Also for lossless encoding you should specify ``chroma=444`` during save.

When use pillow_heif as a plugin you can set it with: `register_*_opener(quality=-1)`"""


SAVE_HDR_TO_12_BIT = False
"""Should 16 bit images be saved to 12 bit instead of 10 bit``

When use pillow_heif as a plugin you can set it with: `register_*_opener(save_to_12bit=True)`"""


SAVE_NCLX_PROFILE = True
"""Should be ``nclx`` profile saved or not.

Default for all previous versions(pillow_heif<0.14.0) was NOT TO save `nclx` profile,
due to an old bug in Apple software refusing to open images with `nclx` profiles.
Apple has already fixed this and there is no longer a need to not save the default profile.

.. note:: `save_nclx_profile` specified during calling ``save`` has higher priority than this.

When use pillow_heif as a plugin you can unset it with: `register_*_opener(save_nclx_profile=False)`"""


PREFERRED_ENCODER = {
    "AVIF": "",
    "HEIF": "",
}
"""Use the specified encoder for format.

You can get the available encoders IDs using ``libheif_info()`` function.

When use pillow_heif as a plugin you can set this option with ``preferred_encoder`` key."""


PREFERRED_DECODER = {
    "AVIF": "",
    "HEIF": "",
}
"""Use the specified decoder for format.

You can get the available decoders IDs using ``libheif_info()`` function.

When use pillow_heif as a plugin you can set this option with ``preferred_decoder`` key."""


DISABLE_SECURITY_LIMITS = False
"""Option to completely disable libheif security limits.

Reference: https://github.com/strukturag/libheif/issues/1275"""


GRID_TILE_SIZE = 0
"""Default tile size for grid encoding.

When set to a positive value, images larger than this size in at least one dimension
will be split into a grid of tiles during encoding. This matches how Apple
devices encode HEIF photos and can improve compression efficiency.

Common values: 512 (Apple default), 256, 1024.
A value of 0 (default) disables grid encoding.
A grid cannot have more than 256 rows or columns and a file cannot have more than 1000 items
in total: tiles, thumbnails and metadata blocks all count. Readers with default libheif
security limits cannot open files with more items.

Images with an alpha channel are always encoded as a single image: libheif stores alpha
only on the individual tiles, where readers like Apple's ImageIO ignore it and render the
image fully opaque. ``AVIF`` images are also encoded as a single image when the grid would
violate MIAF constraints that ``libavif``-based readers enforce: a tile size smaller than 64,
or an odd width, height or tile size together with subsampled chroma. Saving an image in
``YCbCr`` mode with grid encoding enabled raises ``ValueError``.

When use pillow_heif as a plugin you can set it with: `register_*_opener(grid_tile_size=512)`

.. note:: For images that were read from a tiled HEIF file, the source tile size is used
    by default during saving, except for images converted to ``YCbCr`` mode.
    ``tile_size`` specified during calling ``save`` has higher priority."""
