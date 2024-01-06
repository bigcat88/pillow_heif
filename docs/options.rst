.. _options:

Options
-------

.. autodata:: pillow_heif.options.DECODE_THREADS
.. autodata:: pillow_heif.options.THUMBNAILS
.. autodata:: pillow_heif.options.DEPTH_IMAGES
.. autodata:: pillow_heif.options.QUALITY
.. autodata:: pillow_heif.options.SAVE_HDR_TO_12_BIT
.. autodata:: pillow_heif.options.ALLOW_INCORRECT_HEADERS
.. autodata:: pillow_heif.options.SAVE_NCLX_PROFILE
.. autodata:: pillow_heif.options.PREFERRED_ENCODER
.. autodata:: pillow_heif.options.PREFERRED_DECODER

Example of use
""""""""""""""

.. code-block:: python

    import pillow_heif

    pillow_heif.options.THUMBNAILS = False
    pillow_heif.options.DECODE_THREADS = 1

Overriding multiple options at once
"""""""""""""""""""""""""""""""""""

When registering a Pillow plugin with :py:func:`pillow_heif.register_heif_opener` or :py:func:`pillow_heif.register_avif_opener`

.. code-block:: python

    register_heif_opener(thumbnails=False, quality=100, decode_threads=10)
