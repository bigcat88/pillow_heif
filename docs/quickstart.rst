Quickstart
==========

.. _registering-plugin:

Registering plugin
******************

The most quickest way to start is to use it as a Pillow plugin.
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

.. note:: Function :py:func:`~pillow_heif.register_heif_opener` can override default
    :py:class:`~pillow_heif._options.PyLibHeifOptions` if you needed to.

.. code-block:: python

    from PIL import Image
    from pillow_heif import register_heif_opener

    register_heif_opener()
    with Image.open("image.heic") as im:
        im.rotate(45).save("rotated_image.heic")

**More information what functionality does it support as a plugin can be found here:** :py:class:`~pillow_heif.HeifImageFile`

Options
"""""""

Overriding default options

When registering plugin with :py:func:`pillow_heif.register_heif_opener`

.. code-block:: python

    register_heif_opener(thumbnails=False, quality=100)

With call to :py:func:`pillow_heif.options()`

.. code-block:: python

    options().thumbnails = False
    options().quality = 100

Advanced usage
**************

For usage without Pillow plugin as a base, look at examples started with ``reader_``

For using it as a Pillow plugin, refer to Pillow's documentation:
`Pillow Tutorial <https://pillow.readthedocs.io/en/stable/handbook/tutorial.html>`_
and to examples started with ``opener_``.

`Examples <https://github.com/bigcat88/pillow_heif/tree/master/examples>`_
