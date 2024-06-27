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

    .. py:attribute:: info["depth_images"]
        :type: list

        List of :py:class:`~pillow_heif.heif.HeifDepthImage` if any present for image.
        Currently `libheif` does not support writing of them, only reading.

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
