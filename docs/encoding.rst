.. _encoding:

Encoding of images
==================

Current limitations of encoder
""""""""""""""""""""""""""""""

* ``Libheif`` does not support editing files in place(it is not possible just to change metadata)
* ``HEIF`` format does not provide information in what quality image was encoded

Metadata encoding
"""""""""""""""""

All known metadata information in ``info`` dictionary are saved to output image(for both `Pillow` plugin and `HeifFile`).
Those are:
``exif``, ``xmp`` and ``metadata``

So this is valid code for removing EXIF and XMP information:

.. code-block:: python

    image = Image.open(Path("test.heic"))
    image.info["exif"] = None
    image.info["xmp"] = None
    image.save("output.heic")

And this code is valid too:

.. code-block:: python

    image = Image.open(Path("test.heic"))
    image.save("output.heic", exif=None, xmp=None)

Limitations of second code variant is that when file has multiply images inside,
setting ``exif`` or ``xmp`` during ``save`` affects only Primary(Main) image and not all images.

To edit metadata of all images in a file just iterate throw all images and change metadata in place.

Here are two ways for `Pillow`:

For example edit ``info["exif"]`` field of each image copy:

.. code-block:: python

    heic_pillow = Image.open(Path("test.heic"))
    output_wo_exif = []
    for frame in ImageSequence.Iterator(heic_pillow):
        copied_frame = frame.copy()
        copied_frame.info["exif"] = None
        output_wo_exif.append(copied_frame)
    empty_pillow = Image.new("P", (0, 0))
    empty_pillow.save("no_exif.heic", save_all=True, append_images=output_wo_exif)

Or editing ``info["exif"]`` in place(from version `0.3.1`):

.. code-block:: python

    heic_pillow = Image.open(Path("test.heic"))
    for frame in ImageSequence.Iterator(heic_pillow):
        frame.info["exif"] = None
    heic_pillow.save("no_exif.heic", save_all=True)

.. _changing-order-of-images:

Changing order of images
""""""""""""""""""""""""

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
