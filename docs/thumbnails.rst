.. py:currentmodule:: pillow_heif

.. _using-thumbnails:

Using thumbnails
================

Available from version ``0.5.0``

Many HEIF files has in-built thumbnails. It is much faster to decode thumbnail that has lesser size then original.

For easy access for that you can use :py:func:`~pillow_heif.thumbnail`

.. code-block:: python

    heif_file = pillow_heif.open_heif("input.heic")
    heif_image = pillow_heif.thumbnail(heif_file)
    print(heif_image.size, heif_image.mode, len(heif_image.data), heif_image.stride)

Or as a Pillow plugin:

.. code-block:: python

    pil_img = Image.open("input.heic")
    img = pillow_heif.thumbnail(pil_img)
    img.show()

.. note:: For Pillow: image should not be already loaded.
    Who need thumbnail if an original was already decoded?

Function :py:func:`~pillow_heif.thumbnail` has an optional parameter ``min_box``,
so you can specify minimal size of thumbnail you interested in.
Images that come from iPhone usual has thumbnails with 512 box size.
