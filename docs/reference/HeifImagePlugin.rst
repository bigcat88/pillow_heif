Pillow Plugin
=============

HeifImageFile object
--------------------

| Plugin supports decoding and encoding multiply image frames.
| How to register it see: :ref:`registering-plugin`
| It supports all functionality, that supported by other Pillow's image plugins.

.. autoclass:: pillow_heif.HeifImageFile
    :show-inheritance:

.. autoclass:: pillow_heif.as_opener._LibHeifImageFile
    :show-inheritance:
    :members:

    .. py:attribute:: info
        :type: dict

        A dictionary holding data associated with the image.

        .. note::
            Known to this plugin keys and values in dictionary will be saved to the image.
            They are the same as in :py:class:`~pillow_heif.HeifImage` class.

        Specific keys for this plugin that is always present are:
            exif, xmp, metadata, thumbnails, primary
        Optional there can be also such keys:
            icc_profile, icc_profile_type, nclx_profile

    .. py:method:: get_format_mimetype

        Returns the same as :py:func:`~pillow_heif.get_file_mimetype`


Pillow Plugin Manual Registration
---------------------------------

.. autofunction:: pillow_heif.register_heif_opener


If you do not need HEIF thumbnails functionality, then it is a good idea
to disable them during plugin registration:

.. code-block:: python

    register_heif_opener(thumbnails=False)

If you are using another h264(AVIF) plugin, you free to disable AVIF decoding support:

.. code-block:: python

    register_heif_opener(avif=False)

Remember, then you can pass multiply config values to :py:func:`~pillow_heif.register_heif_opener` at once:

.. code-block:: python

    register_heif_opener(thumbnails=False, avif=False)
