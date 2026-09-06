.. py:currentmodule:: pillow_heif

HeifImage object
================

.. autoclass:: pillow_heif.HeifImage
    :show-inheritance:
    :inherited-members:
    :members:

    .. describe:: info["exif"]: bytes

        .. note:: In HEIF `orientation` tag is only for information purposes and must not be used to rotate image.

        EXIF metadata. Can be `None`

    .. describe:: info["xmp"]: bytes

        XMP metadata. String in bytes in UTF-8 encoding. Absent if `xmp` data is missing.

    .. describe:: info["metadata"]: list[dict]

        Other metadata(IPTC for example). List of dictionaries. Usual will be empty. Keys:

            * `type`: str
            * `content_type`: str
            * `data`: bytes

    .. describe:: info["primary"]: bool

        A boolean value that specifies whether the image is the main image when the file
        contains more than one image.

    .. describe:: info["bit_depth"]: int

        Shows the bit-depth of image in file(not the decoded one, so it may differs from bit depth of mode).
        Possible values: 8, 10 and 12.

    .. describe:: info["chroma"]: int

        Chroma subsampling of the image in file. Possible values: 420, 422 and 444.
        Absent for monochrome images.

    .. describe:: info["thumbnails"]: list[int]

        List of thumbnail boxes sizes. Can be empty.

    .. describe:: info["icc_profile"]: bytes

        ICC Profile. Can be absent. Can be empty.

    .. describe:: info["icc_profile_type"]: str

        Possible values: ``prof`` or ``rICC``. Can be absent.

    .. describe:: info["nclx_profile"]: dict

        NCLX color profile. Can be absent. Keys:

            * `color_primaries`: :py:class:`HeifColorPrimaries`
            * `transfer_characteristics`: :py:class:`HeifTransferCharacteristics`
            * `matrix_coefficients`: :py:class:`HeifMatrixCoefficients`
            * `full_range_flag`: `bool`

    .. describe:: info["content_light_level"]: dict

        Content light level information(``clli``). Can be absent. Keys:

            * `max_content_light_level`: `int`
            * `max_pic_average_light_level`: `int`

    .. describe:: info["mastering_display_colour_volume"]: dict

        Mastering display colour volume(``mdcv``). Can be absent. Keys:

            * `display_primaries_x`: `tuple[int, int, int]`
            * `display_primaries_y`: `tuple[int, int, int]`
            * `white_point_x`: `int`
            * `white_point_y`: `int`
            * `max_display_mastering_luminance`: `int`
            * `min_display_mastering_luminance`: `int`

    .. describe:: info["ambient_viewing_environment"]: dict

        Ambient viewing environment(``amve``). Can be absent. Keys:

            * `ambient_illumination`: `int`
            * `ambient_light_x`: `int`
            * `ambient_light_y`: `int`

        .. note:: These three properties hold the raw code values as defined in ITU-T H.274.
            Like ``nclx_profile`` and ``icc_profile`` they are written back during save;
            remove a key from ``info`` if you do not want it in the output file.

    .. describe:: info["nominal_diffuse_white_luminance"]: int

        Nominal diffuse white luminance(``ndwt``) in units of 0.0001 candelas per square metre.
        Can be absent; ``0`` is a valid value and selects the default definition of ISO/TS 22028-5.
        It is written back during save; remove the key from ``info`` if you do not want it
        in the output file.

    .. describe:: info["pixel_aspect_ratio"]: tuple[int, int]

        Pixel aspect ratio(``pasp``) as ``(horizontal_spacing, vertical_spacing)``.
        Absent when the image has no ``pasp`` box. It is written back during save.

    .. describe:: info["depth_images"]: list

        List of :py:class:`~pillow_heif.heif.HeifDepthImage` if any present for image.
        Currently `libheif` does not support writing of them, only reading.

    .. describe:: info["aux"]: dict

        Auxiliary images present for the image. Keys are the auxiliary types, e.g.
        ``urn:com:apple:photo:2020:aux:hdrgainmap``, values are lists of IDs to pass to
        :py:meth:`~pillow_heif.HeifImage.get_aux_image`. Empty when the image has no auxiliary images.
        Currently `libheif` does not support writing of them, only reading.

    .. describe:: info["tiling"]: dict

        Tiling information when the image is stored as a grid of tiles. Absent for non-tiled images.
        All values are in the display space, the same as ``size``. Keys:

            * `num_columns`: `int`
            * `num_rows`: `int`
            * `tile_width`: `int`
            * `tile_height`: `int`
            * `image_width`: `int`
            * `image_height`: `int`

    .. describe:: info["heif"]: dict

        Camera matrices of the image, present only when the file contains them. Keys:

            * `camera_intrinsic_matrix`: `dict` with `focal_length_x`, `focal_length_y`,
              `principal_point_x`, `principal_point_y` and `skew`
            * `camera_extrinsic_matrix_rot`: `tuple` of nine `float`, the rotation matrix

        .. note:: These values are currently not written back during save.

    .. describe:: info["entity_groups"]: list

        Entity groups(``grpl``) of the file the image was read from, every image of the file gets the same list.
        Absent when the file has no entity groups. Each group is a dict with keys:

            * `id`: `int`, the group ID
            * `type`: `str`, four-character group type, e.g. ``ster`` for a stereo pair
            * `entities`: `list[int]`, item IDs of the group members in the order stored in the file.
              For ``ster`` the first one is the left view and the second one is the right view.
            * `images`: `list[int | None]`, the same members as indexes of the images in
              :py:class:`~pillow_heif.HeifFile` (frame numbers in Pillow) at the time the file was opened,
              ``None`` for members that are not top-level images

        .. note:: Only group types known to `libheif` are reported, as of libheif 1.23 these are
            ``altr``, ``ster`` and ``pymd``. Entity groups are not written back during save.

.. autoclass:: pillow_heif.heif.BaseImage
    :show-inheritance:
    :inherited-members:
    :members:

.. autoclass:: pillow_heif.heif.HeifDepthImage
    :show-inheritance:
    :inherited-members:
    :members:

    .. describe:: info["metadata"]: dict

        Represents `libheif` ``heif_depth_representation_info`` struct as a dictionary.

        If someone have an example when this struct got filled let me know.

.. autoclass:: pillow_heif.heif.HeifAuxImage
    :show-inheritance:
    :inherited-members:
    :members:
