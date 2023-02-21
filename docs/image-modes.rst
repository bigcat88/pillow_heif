.. _image-modes:

Modes
=====

Possible :py:attr:`~pillow_heif.HeifImage.mode` modes are:

    * ``BGRA;16`` or ``BGRa;16``
    * ``BGR;16``
    * ``RGBA;16`` or ``RGBa;16``
    * ``RGB;16``
    * ``L;16``
    * ``LA;16``
    * ``I;16``
    * ``I;16L``
    * ``BGRA`` or ``BGRa``
    * ``BGR``
    * ``RGBA`` or ``RGBa``
    * ``RGB``
    * ``LA``
    * ``L``

.. note:: By default ``convert_hdr_to_8bit`` parameter in ``open_heif`` is ``True`` so all images will be opened as a 8 bit ones.
    To open images in `BGR` mode, set ``bgr_mode`` to `True` in ``open_heif``.

When saving image from `Pillow` to `HEIF` format, next modes will be converted automatically before encoding:

    * ``P`` with transparency will be converted to ``RGBA``
    * ``P`` will be converted to ``RGB``
    * ``I`` will be converted to ``I;16L``
    * ``1`` will be converted to ``L``
    * ``CMYK`` will be converted to ``RGBA``
