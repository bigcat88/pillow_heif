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

Arrow C data interface
----------------------

Images decoded from a file implement the `Arrow PyCapsule interface
<https://arrow.apache.org/docs/format/CDataInterface/PyCapsuleInterface.html>`_:
:py:class:`~pillow_heif.HeifImage`, :py:class:`~pillow_heif.heif.HeifDepthImage` and
:py:class:`~pillow_heif.heif.HeifAuxImage` can be given to ``Image.fromarrow``, ``pyarrow.array``
or any other Arrow consumer without copying the decoded data. This is also what
:py:meth:`~pillow_heif.HeifImage.to_pillow` uses to share the decoded plane with the created
image when the file was opened with the ``pillow_layout`` option.

The exported array is flat: `width * height * channels` values of ``uint8``, where an 8-bit
``RGB`` image decoded with ``pillow_layout`` has four values per pixel with the fourth one unused.
16-bit images are exported as ``int16`` — the format `Pillow` itself uses for ``I;16`` images —
so an Arrow consumer that does arithmetic on the values should reinterpret them as ``uint16``,
otherwise values above `32767` will be read as negative.

.. note:: `Pillow` has no 16-bit multichannel modes, so of the 16-bit images only the single
    channel ``I;16`` ones can be given to it; ``RGB;16``/``RGBA;16`` images export the same way,
    but for consumers like `PyArrow`.

The consumer must treat the data as read-only, and the data keeps the decoded image alive for
as long as it is used. When an image was decoded with ``remove_stride=False`` and its rows got
padded, there is no flat data to export and ``ValueError`` is raised.

.. automethod:: pillow_heif.HeifImage.__arrow_c_schema__
.. automethod:: pillow_heif.HeifImage.__arrow_c_array__

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
