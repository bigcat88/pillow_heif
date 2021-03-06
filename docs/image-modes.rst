.. _image-modes:

Modes
=====

Most of modes are new and supported only from version ``0.4.0``

Possible :py:attr:`~pillow_heif.HeifImage.mode` modes are:

    * ``BGRA;16``
    * ``BGR;16``
    * ``RGBA;16``
    * ``RGB;16``
    * ``L;16``
    * ``I;16``
    * ``I;16L``
    * ``BGRA;12``
    * ``BGR;12``
    * ``RGBA;12`` (default mode for ``HeifFile`` when image is 12 bit with alpha channel)
    * ``RGB;12`` (default mode for ``HeifFile`` when image is 12 bit)
    * ``L;12``
    * ``I;12``
    * ``I;12L``
    * ``BGRA;10``
    * ``BGR;10``
    * ``RGBA;10`` (default mode for ``HeifFile`` when image is 10 bit with alpha channel)
    * ``RGB;10`` (default mode for ``HeifFile`` when image is 10 bit)
    * ``L;10``
    * ``I;10``
    * ``I;10L``
    * ``BGRA``
    * ``BGR``
    * ``RGBA`` (default mode for ``HeifFile`` when image is 8 bit with alpha channel)
    * ``RGB`` (default mode for ``HeifFile`` when image is 8 bit)
    * ``L``

.. note:: By default ``convert_hdr_to_8bit`` parameter in ``open_heif`` is ``True`` so all images will be opened as a 8 bit ones.

When saving image from `Pillow` to `HEIF` format, next modes will be converted automatically before encoding:

    * ``LA`` (will be converted to ``RGBA``)
    * ``PA`` (will be converted to ``RGBA``)
    * ``P`` (will be converted to ``RGB``)
    * ``I`` (will be converted to ``I;16L``)
    * ``1`` (will be converted to ``L``)

.. _convert_to:

Mode conversion
---------------

For ``HeifFile`` some of these modes can be converted to each other using :py:meth:`~pillow_heif.HeifImage.convert_to` method:

    * ``BGRA;16``  -->  ``RGBA;10`` or ``RGBA;12``
    * ``BGR;16``  -->  ``RGB;10`` or ``RGB;12``
    * ``RGBA;16``  -->  ``RGBA;10`` or ``RGBA;12``
    * ``RGB;16``  -->  ``RGB;10`` or ``RGB;12``
    * ``L;16``  -->  ``L;10`` or ``L;12``
    * ``I;16``  -->  ``L;10`` or ``L;12``
    * ``I;16L``  -->  ``L;10`` or ``L;12``
    * ``RGBA;12``  -->  ``RGBA;16`` or ``BGRA;16``
    * ``RGB;12``  -->  ``RGB;16`` or ``BGR;16``
    * ``RGBA;10``  -->  ``RGBA;16`` or ``BGRA;16``
    * ``RGB;10``  -->  ``RGB;16`` or ``BGR;16``
    * ``BGRA``  -->  ``RGBA``
    * ``BGR``  -->  ``RGB``
    * ``RGBA``  -->  ``BGRA``, ``RGBA;16`` or ``BGRA;16``
    * ``RGB``  -->  ``BGR``, ``RGB;16`` or ``BGR;16``

.. note:: HEIF standard does not support 16 bit images, see :ref:`saving-16bit`
