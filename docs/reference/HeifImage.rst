.. py:currentmodule:: pillow_heif

HeifImage class object
======================

.. autoclass:: pillow_heif.HeifImage
    :show-inheritance:
    :inherited-members:
    :members:

    .. autoattribute:: size

    .. py:attribute:: info["exif"]
        :type: bytes

        .. note:: In HEIF `orientation` tag is only for information purposes and must not be used to rotate image.

        EXIF metadata. Can be `None`

    .. py:attribute:: info["xmp"]
        :type: bytes

        XMP metadata. Can be `None`

    .. py:attribute:: info["metadata"]
        :type: list

        IPTC metadata. Usual will be an empty list.

    .. py:attribute:: info["icc_profile"]
        :type: bytes

        ICC Profile. Can be absent.

    .. py:attribute:: info["icc_profile_type"]
        :type: str

        Possible values: ``prof`` or ``rICC``. Can be absent.

    .. py:attribute:: info["nclx_profile"]
        :type: bytes

        Can be absent. Maybe later, will be added some stuff to work with nclx profiles.

        If you need it now, look at `heif.h` for struct describing it in ``C`` language.
