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
