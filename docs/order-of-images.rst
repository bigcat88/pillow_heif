.. _order-of-images:

Order Of Images
===============

All information here is only for files that has multiply images and when first image in file is not a `PrimaryImage`

Versions <0.3.0
***************

Old behaviour was that the first image was always primary, no matter in which position it was in file.
And during saving, first image was always primary.
You can take a look at these two files:

This is the original `nokia:alpha.heic <https://insert_link>`_

This file was created from it with thumbnails added: `nokia:alpha_with_thumbs.heic <https://insert_link>`_

As you can see, third image that is `primary` image in that container switched from pos 3, to pos 1 after saving.
Not a big deal, but it can be considered as a small little bug in some cases.

Here is the code from versions till `0.3.0`:

.. code-block:: python

    main_image_id = heif_ctx.get_main_img_id()
    top_img_ids = heif_ctx.get_top_images_ids()
    top_img_list = [main_image_id] + [i for i in top_img_ids if i != main_image_id]

Reworked image order handling
*****************************

Reading
"""""""

Easiest way to handle this for usage **not** as a Pillow plugin is to change :py:class:`~pillow_heif.HeifFile`
that it will point as in old versions to `primary` image, but not to place that image as first in `top_img_list`.

So this code will be equal in both old and new versions:

.. code-block:: python

    heif_file = open_heif("input.hec")
    print(heif_file.mode, heif_file.size)

And this will have different behaviour:

.. code-block:: python

    heif_file = open_heif("input.hec")
    print(heif_file[0].mode, heif_file[0].size)

For Pillow plugin this will be a bit break change when you use it to work with image containers,
cause from this change if you need to find a primary image you need to iterate throw all images and find image with
`info["primary"]=True`.

Writing
"""""""

In `0.2.x` versions when encoder was introduced, there was no way to create a file with primary image that is not in a first place.

From now, first image will be `primary`, unless after first image there is no images with `info["primary"]` set to ``True``.
So, last image with `info["primary"]` == ``True`` will be the primary image, .

In most cases you do not need to bother yourself with this, as other image formats are much simpler and has no such abilities
and when converting to `HEIF` it will just worked as before.

Converting from `HEIF` to `HEIF` will work as before, no any changes for both `HeifFile` or `Pillow plugin` usage part,
it will just place primary image position as it was in original image and do it right.

When you need to change `primary` image for some reason, just set `info["primary"]` of image to ``True``
and all images after that should not have `info["primary"]` or `info["primary"]` == ``True``.

That's all.
