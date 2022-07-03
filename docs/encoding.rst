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
