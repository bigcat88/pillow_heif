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
            exif, metadata, primary, bit_depth, thumbnails, depth_images, aux, original_orientation
        Optional there can be also such keys:
            xmp, chroma, icc_profile, icc_profile_type, nclx_profile, content_light_level,
            mastering_display_colour_volume, ambient_viewing_environment, nominal_diffuse_white_luminance,
            pixel_aspect_ratio, tiling, heif, entity_groups

    .. describe:: info["original_orientation"]: int

        Orientation that the ``EXIF``/``XMP`` tags had in the file, or ``None`` when there was none.
        The plugin calls :py:func:`~pillow_heif.set_orientation` for every image, so the tags
        themselves are already reset when the image is opened, see :doc:`/workaround-orientation`.

    .. py:method:: get_format_mimetype

        Returns the same as :py:func:`~pillow_heif.get_file_mimetype`

.. autoclass:: pillow_heif.HeifImageFile
    :show-inheritance:

.. autofunction:: pillow_heif.register_heif_opener
