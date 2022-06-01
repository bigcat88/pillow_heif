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
To edit metadata of all images in a file just iterate throw all images and change metadata you want.


To be continued...
