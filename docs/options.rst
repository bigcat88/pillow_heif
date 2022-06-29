.. py:currentmodule:: pillow_heif

Options
-------

.. autofunction:: options
.. autoclass:: pillow_heif._options.PyLibHeifOptions
    :members:

Overriding default options
""""""""""""""""""""""""""

When registering a Pillow plugin with :py:func:`pillow_heif.register_heif_opener`

.. code-block:: python

    register_heif_opener(thumbnails=False, quality=100)

With call to :py:func:`pillow_heif.options()`

.. code-block:: python

    options().thumbnails = False
    options().quality = 100
