Pillow Plugin
=============

HeifImageFile object
--------------------

| Plugin supports decoding and encoding multiply image frames.
| How to register it see: :ref:`registering-plugin`
| It supports all functionality, that supported by other Pillow's image plugins.

.. autoclass:: pillow_heif.as_plugin._LibHeifImageFile
    :show-inheritance:
    :members:

    .. py:attribute:: info
        :type: dict

        A dictionary holding data associated with the image.

        .. note::
            Known to this plugin keys and values in dictionary will be saved to the image.
            They are the same as in :py:class:`~pillow_heif.HeifImage` class.

        Specific keys for this plugin that is always present are:
            exif, xmp, metadata, primary, bit_depth, thumbnails
        Optional there can be also such keys:
            icc_profile, icc_profile_type, nclx_profile

    .. py:method:: get_format_mimetype

        Returns the same as :py:func:`~pillow_heif.get_file_mimetype`

.. autoclass:: pillow_heif.HeifImageFile
    :show-inheritance:

.. autoclass:: pillow_heif.AvifImageFile
    :show-inheritance:

.. autofunction:: pillow_heif.register_heif_opener

.. autofunction:: pillow_heif.register_avif_opener
