.. _saving-images:

Saving images
=============

Current limitations of encoder
""""""""""""""""""""""""""""""

* ``Libheif`` does not support editing files in place(it is not possible just to change metadata)
* ``HEIF`` format does not provide information in what quality image was encoded


.. _save-parameters:

Save parameters
"""""""""""""""

Method ``save`` in both ``HeifFile`` and ``Pillow`` supports the **same** parameters.
There is only two differences between them:

* Pillow's ``save`` by default has ``save_all=False`` and ``HeifFile`` has ``save_all=True``
* When saving to memory for ``HeifFile`` you do not need to specify ``format`` parameter.

Here is description of it: :py:meth:`~pillow_heif.HeifFile.save`

.. _saving-16bit:

Saving 16 bit images
""""""""""""""""""""

All 16 bit images that was created with:

* :py:meth:`~pillow_heif.HeifFile.add_from_pillow`
* :py:meth:`~pillow_heif.HeifFile.add_frombytes`
* or images opened in ``I`` Pillow modes when using as a Pillow plugin

Will be saved by default in 10 bit mode.

To ``save`` 16 bit image in 12 bit set ``options().save_to_12bit`` to ``True``.

Images opened from file will be saved based on ``info["bit_depth"]`` value if it is present.

.. _order-of-images:

Order Of Images
"""""""""""""""

All information here is only for files that has multiply images and when first image in file is not a `PrimaryImage`

Lets imagine that we have file with 3 images and second image in file is a primary image.

.. code-block:: python

    im = open_heif("image.heif")
    im_pil = Image.open("image.heif")

Both ``im`` and ``im_pil`` points to the second image in file, that is a primary image.

This asserts will pass:

.. code-block:: python

    assert im.info["primary"] == True
    assert im[0].info["primary"] == False
    assert im[1].info["primary"] == True
    assert im[2].info["primary"] == False

    assert im_pil.info["primary"] == True
    im_pil.seek(0)
    assert im_pil.info["primary"] == False
    im_pil.seek(1)
    assert im_pil.info["primary"] == True
    im_pil.seek(2)
    assert im_pil.info["primary"] == False

And next code will produce the same behavior results(during enumerating all frames):

.. code-block:: python

    for frame in im:
        print(frame.mode, frame.size)

    for frame in ImageSequence.Iterator(im_pil):
        print(frame.mode, frame.size)

Primary image when saving image sequences
"""""""""""""""""""""""""""""""""""""""""

First image will be `primary`, unless after first image there is no images with `info["primary"]` set to ``True``.
So, last image with `info["primary"]` == ``True`` will be the primary image.

In most cases you do not need to bother yourself with this, as other image formats are much simpler and has no such abilities.

When you need to change `primary` image for some reason, just set `info["primary"]` of image to ``True``
and all images after that should not have `info["primary"]` == ``True``.

Method ``save`` supports ``primary_index`` parameter, that accepts ``index of image`` or ``-1`` to set last image as `PrimaryImage`.

Specifying ``primary_index`` during ``save`` has highest priority.

NCLX color profile
""""""""""""""""""

By default, since version **0.14.0**, if the image already had an NCLX color profile, it will be saved during encoding.

.. note:: If you need old behaviour and for some reason do not need `NCLX` profile be saved you can set global option ``SAVE_NCLX_PROFILE`` to ``False``.

To change it, you can specify your values for NCLX color conversion for ``save`` operation in two ways.

Set `output` NCLX profile:

    .. note:: Avalaible only from **0.14.0** version.

    .. code-block:: python

        buf = BytesIO()
        im.save(buf, format="HEIF", matrix_coefficients=0, color_primaries=1)

    In this case the default output NCLX profile will be created, and values you provide in such way,
    will replace the values from default output profile.

Edit NCLX profile in `image.info`:

    .. code-block:: python

        buf = BytesIO()
        im.info["nclx_profile"]["matrix_coefficients"] = 0  # code assumes that image has already "nclx_profile"
        im.info["nclx_profile"]["color_primaries"] = 1
        im.save(buf, format="HEIF")

    Under the hood it is much complex, as second way will change the **input** NCLX profile.

The preferable way is to specify new NCLX values during ``save``.

Here is additional info, from the **libheif repo** with relevant information:

https://github.com/strukturag/libheif/discussions/931
https://github.com/strukturag/libheif/issues/995

Lossless encoding
"""""""""""""""""

.. note:: Parameter ``matrix_coefficients`` avalaible only from **0.14.0** version.

Although the HEIF format is not intended for lossless encoding, it is possible with some encoders that support it.

You need to specify ``matrix_coefficients=0``
(which will tell **libheif** to perform the conversion in the RGB color space) and chrome subsampling equal to "4:4:4".

.. code-block:: python

    im_rgb = Image.merge(
        "RGB",
        [
            Image.linear_gradient(mode="L"),
            Image.linear_gradient(mode="L").transpose(Image.ROTATE_90),
            Image.linear_gradient(mode="L").transpose(Image.ROTATE_180),
        ],
    )
    buf = BytesIO()
    im_rgb.save(buf, format="HEIF", quality=-1, chroma=444, matrix_coefficients=0)

That's all.
