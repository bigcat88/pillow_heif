Encoding of images
==================

Current limitations of encoder
""""""""""""""""""""""""""""""

* ``Libheif`` does not support editing files in place(it is not possible just to change metadata)
* ``HEIF`` format does not provide information in what quality image was encoded

Metadata encoding
"""""""""""""""""

All known metadata information in ``image.info`` dictionary are saved to output image.
Those are:
``exif``, ``xmp`` and ``metadata``

So this is valid code for removing EXIF information:

.. code-block:: python

    image = Image.open(Path("test.heic"))
    image.info["exif"] = None
    image.save("output.heic")

And this code is valid too:

.. code-block:: python

    image = Image.open(Path("test.heic"))
    image.save("output.heic", exif=None)

Limitations of second code variant is that when file has multiply images inside,
setting ``exif`` during save affects only Primary(Main) image and not all images.

To edit metadata of all images in a file just iterate throw all images and change metadata you want(do not work for Pillow plugin).

When you want edit metadata when using as Pillow plugin for all images you can do something like this(editing ``info["exif"]`` field of each image):

.. code-block:: python

    heic_pillow = Image.open(Path("test.heic"))
    output_wo_exif = []
    for frame in ImageSequence.Iterator(heic_pillow):
        copied_frame = frame.copy()
        copied_frame.info["exif"] = None
        output_wo_exif.append(copied_frame)
    empty_pillow = Image.new("P", (0, 0))
    empty_pillow.save("no_exif.heic", save_all=True, append_images=output_wo_exif)

.. _changing-order-of-images:

Changing order of images
""""""""""""""""""""""""

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

And here is an example how we can change order of images in container:

.. code-block:: python

    src_img = Image.open(Path("1_2_3P.heic"))
    img3 = ImageSequence.Iterator(src_img)[2].copy()
    img2 = ImageSequence.Iterator(src_img)[1].copy()
    img1 = ImageSequence.Iterator(src_img)[0].copy()
    img3.save("3P_1_2.heic", save_all=True, append_images=[img1, img2], quality=-1)
