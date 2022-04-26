.. py:currentmodule:: pillow_heif

.. _advanced-usage:

Tutorial
========

Open image
----------

.. code-block:: python

    from pillow_heif import open_heif, is_supported

    if is_supported("image.heif"):
        heif_file = open_heif("image.heif")

If successful, it will return :py:class:`~pillow_heif.HeifFile` object.
After that let's get some basic info about it:

.. code-block:: python

    print("mimetype:", heif_file.mimetype)
    print("Number of images:", len(heif_file))
    print("Number of thumbnails:", len(list(heif_file.thumbnails_all())))

After that lets print information about each image in file:

.. code-block:: python

    for image in heif_file:
        print("\tDepth:", image.bit_depth)
        print("\tMode:", image.mode)
        print("\tAlpha:", image.has_alpha)
        print("\tSize:", image.size)
        print("\tStride:", image.stride)
        print("\tChroma:", image.chroma)
        print("\tColor:", image.color)

Will continue...

Full example can be found here:
`Print Heif Info <https://github.com/bigcat88/pillow_heif/blob/master/examples/dump_heif_info.py>`_
