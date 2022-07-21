.. _encoding:

Encoding of images
==================

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

* :py:meth:`~pillow_heif.HeifImage.convert_to`
* :py:meth:`~pillow_heif.HeifFile.add_from_pillow`
* :py:meth:`~pillow_heif.HeifFile.add_frombytes`
* or images opened in ``I`` Pillow modes when using as a Pillow plugin

Will be saved by default in 10 bit mode.

To ``save`` 16 bit image in 12 bit for you can convert it to 12 bit before saving or set ``options().save_to_12bit`` to ``True``.

.. _order-of-images:

Order Of Images
"""""""""""""""

All information here is only for files that has multiply images and when first image in file is not a `PrimaryImage`

There was a slightly different behaviour in 0.2.x versions and 0.3.0 - 0.4.0 versions.
Starting from version `0.5.0` ``pillow-heif`` in both ``Pillow`` and ``stand alone`` mode works the same way.

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

That's all.
