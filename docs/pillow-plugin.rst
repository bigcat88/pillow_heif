Pillow Plugin
=============

For using it as a Pillow plugin, refer to Pillow's documentation:
`Pillow Tutorial <https://pillow.readthedocs.io/en/stable/handbook/tutorial.html>`_
and to examples started with ``pillow_``.

Here are described only some differences and peculiarities.

.. _registering-plugin:

Registering plugin
******************

There are two ways to register it as a plugin, here are both of them:

Automatic
"""""""""

.. code-block:: python

    from PIL import Image, ImageFilter
    from pillow_heif import HeifImagePlugin

    with Image.open("image.heic") as im:
        im.filter(filter=ImageFilter.BLUR).save("blurred_image.heic")

Manual
""""""

.. code-block:: python

    from PIL import Image
    from pillow_heif import register_heif_opener

    register_heif_opener()
    with Image.open("image.heic") as im:
        im.rotate(45).save("rotated_image.heic")

AVIF plugin
"""""""""""

``AVIF`` plugin can be registered the same way as ``HEIF``:

.. code-block:: python

    from pillow_heif import register_avif_opener

    register_avif_opener()

``AVIF`` plugin should support all operations and work the same way as ``HEIF`` plugin do.

.. note:: Deprecated, use the `pillow-avif-plugin <https://github.com/fdintino/pillow-avif-plugin>`_ project instead.

Tips & Tricks
"""""""""""""

If you do not need HEIF thumbnails functionality, then it is a good idea
to disable them during plugin registration:

.. code-block:: python

    register_heif_opener(thumbnails=False)

Remember, then you can pass multiply config values to :py:func:`~pillow_heif.register_heif_opener` at once:

.. code-block:: python

    register_heif_opener(thumbnails=False, quality=-1)

.. note:: :py:func:`~pillow_heif.register_avif_opener` works in the same way.

Image Modes
***********

Currently all images are opened in ``RGB`` or ``RGBA`` 8 bit modes.
There is a restriction in ``libheif`` that we cant check before decoding if an image is ``monochrome`` or not.

See :ref:`image-modes` for a list of supported modes for saving.

Metadata
********

Available metadata are stored in ``info`` dictionary as in other Pillow plugins.

It is the same as in :py:class:`~pillow_heif.HeifImage` class.

During saving operation all known metadata in ``info`` dictionary are **saved**.
So it can be edited in place.

Removing EXIF and XMP information inside ``info`` dictionary:

.. code-block:: python

    image = Image.open(Path("test.heic"))
    del image.info["exif"]
    del image.info["xmp"]
    image.save("output.heic")

Removing EXIF and XMP specifying them when calling ``save``:

.. code-block:: python

    image = Image.open(Path("test.heic"))
    image.save("output.heic", exif=None, xmp=None)

Limitations of second code variant is that when file has multiply images inside,
setting ``exif`` or ``xmp`` during ``save`` affects only Primary(Main) image and not all images.

To edit metadata of all images in a file just iterate throw all images and change metadata in place.

Here are two ways as an example:

Edit ``info["exif"]`` field of each copy of image:

.. code-block:: python

    heic_pillow = Image.open(Path("test.heic"))
    output_wo_exif = []
    for frame in ImageSequence.Iterator(heic_pillow):
        copied_frame = frame.copy()
        copied_frame.info["exif"] = None
        output_wo_exif.append(copied_frame)
    empty_pillow = Image.new("P", (0, 0))
    empty_pillow.save("no_exif.heic", save_all=True, append_images=output_wo_exif)

Or editing ``info["exif"]`` in place:

.. code-block:: python

    heic_pillow = Image.open(Path("test.heic"))
    for frame in ImageSequence.Iterator(heic_pillow):
        frame.info["exif"] = None
    heic_pillow.save("no_exif.heic", save_all=True)

Save operation
**************

For `HEIF` next extensions are registered: ``.heic``, ``.heics``, ``.heif``, ``.heifs`` and ``.hif``

For `AVIF` registered extensions are: ``.avif``

Also images can be saved to memory, using ``format`` parameter:

.. code-block:: python

    output_buffer = BytesIO()
    with Image.open("image.heic") as im:
        im.save(output_buffer, format="HEIF")

See here :ref:`save-parameters` for additional information.

Changing order of images
************************

There is no such easy way to change order as for `HeifFile` usage, but the standard Pillow way to do so looks fine.
Let's create image where second image will be primary:

.. code-block:: python

    img1 = Image.open(Path("images/jpeg_gif_png/1.png"))
    img2 = Image.open(Path("images/jpeg_gif_png/2.png"))
    img3 = Image.open(Path("images/jpeg_gif_png/3.png"))
    img1.save("1_2P_3.heic", append_images=[img2, img3], save_all=True, primary_index=1, quality=-1)

Now as example lets change primary image in a HEIC file:

.. code-block:: python

    img1 = Image.open(Path("1_2P_3.heic"))
    img1.save("1_2_3P.heic", save_all=True, primary_index=-1, quality=-1)

.. note::

    As a ``primary`` field are in `info` dictionary, you can change it in a place like with metadata before.

And here is an example how we can change order of images in container:

.. code-block:: python

    src_img = Image.open(Path("1_2_3P.heic"))
    img3 = ImageSequence.Iterator(src_img)[2].copy()
    img2 = ImageSequence.Iterator(src_img)[1].copy()
    img1 = ImageSequence.Iterator(src_img)[0].copy()
    img3.save("3P_1_2.heic", save_all=True, append_images=[img1, img2], quality=-1)
