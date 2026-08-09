.. py:currentmodule:: pillow_heif

HeifImage object
================

.. autoclass:: pillow_heif.HeifImage
    :show-inheritance:
    :inherited-members:
    :members:

    .. py:attribute:: info["exif"]
        :type: bytes

        .. note:: In HEIF `orientation` tag is only for information purposes and must not be used to rotate image.

        EXIF metadata. Can be `None`

    .. py:attribute:: info["xmp"]
        :type: bytes

        XMP metadata. String in bytes in UTF-8 encoding. Absent if `xmp` data is missing.

    .. py:attribute:: info["metadata"]
        :type: list[dict]

        Other metadata(IPTC for example). List of dictionaries. Usual will be empty. Keys:

            * `type`: str
            * `content_type`: str
            * `data`: bytes

    .. py:attribute:: info["primary"]
        :type: bool

        A boolean value that specifies whether the image is the main image when the file
        contains more than one image.

    .. py:attribute:: info["bit_depth"]
        :type: int

        Shows the bit-depth of image in file(not the decoded one, so it may differs from bit depth of mode).
        Possible values: 8, 10 and 12.

    .. py:attribute:: info["thumbnails"]
        :type: list[int]

        List of thumbnail boxes sizes. Can be empty.

    .. py:attribute:: info["icc_profile"]
        :type: bytes

        ICC Profile. Can be absent. Can be empty.

    .. py:attribute:: info["icc_profile_type"]
        :type: str

        Possible values: ``prof`` or ``rICC``. Can be absent.

    .. py:attribute:: info["nclx_profile"]
        :type: dict

        NCLX color profile. Can be absent. Keys:

            * `color_primaries`: :py:class:`HeifColorPrimaries`
            * `transfer_characteristics`: :py:class:`HeifTransferCharacteristics`
            * `matrix_coefficients`: :py:class:`HeifMatrixCoefficients`
            * `full_range_flag`: `bool`

    .. py:attribute:: info["content_light_level"]
        :type: dict

        Content light level information(``clli``). Can be absent. Keys:

            * `max_content_light_level`: `int`
            * `max_pic_average_light_level`: `int`

    .. py:attribute:: info["mastering_display_colour_volume"]
        :type: dict

        Mastering display colour volume(``mdcv``). Can be absent. Keys:

            * `display_primaries_x`: `tuple[int, int, int]`
            * `display_primaries_y`: `tuple[int, int, int]`
            * `white_point_x`: `int`
            * `white_point_y`: `int`
            * `max_display_mastering_luminance`: `int`
            * `min_display_mastering_luminance`: `int`

    .. py:attribute:: info["ambient_viewing_environment"]
        :type: dict

        Ambient viewing environment(``amve``). Can be absent. Keys:

            * `ambient_illumination`: `int`
            * `ambient_light_x`: `int`
            * `ambient_light_y`: `int`

        .. note:: These three properties hold the raw code values as defined in ITU-T H.274.
            Like ``nclx_profile`` and ``icc_profile`` they are written back during save;
            remove a key from ``info`` if you do not want it in the output file.

    .. py:attribute:: info["depth_images"]
        :type: list

        List of :py:class:`~pillow_heif.heif.HeifDepthImage` if any present for image.
        Currently `libheif` does not support writing of them, only reading.

    .. py:attribute:: info["tiling"]
        :type: dict

        Tiling information when the image is stored as a grid of tiles. Absent for non-tiled images.
        All values are in the display space, the same as ``size``. Keys:

            * `num_columns`: `int`
            * `num_rows`: `int`
            * `tile_width`: `int`
            * `tile_height`: `int`
            * `image_width`: `int`
            * `image_height`: `int`

.. autoclass:: pillow_heif.heif.BaseImage
    :show-inheritance:
    :inherited-members:
    :members:

.. autoclass:: pillow_heif.heif.HeifDepthImage
    :show-inheritance:
    :inherited-members:
    :members:

    .. py:attribute:: info["metadata"]
        :type: dict

        Represents `libheif` ``heif_depth_representation_info`` struct as a dictionary.

        If someone have an example when this struct got filled let me know.
