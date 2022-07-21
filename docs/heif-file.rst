Using HeifFile
==============

Opening
-------

.. code-block:: python

    if pillow_heif.is_supported("image.heif"):
        heif_file = pillow_heif.open_heif("image.heif")

``open_heif`` is preferred over ``read_heif``, it does not decode images immediatly.
All image data supports `lazy loading` and will be automatically decoded when you request it,
e.g. when access to ``data`` or ``stride`` properties occurs.

Creating from Pillow
--------------------

.. code-block:: python

    heif_file = pillow_heif.from_pillow(Image.open("image.gif")):

You can specify ``load_one=True`` if you need to add only one frame from a multi-frame image.

Creating from bytes
-------------------

.. code-block:: python

    import cv2  # OpenCV

    cv_img = cv2.imread("image_16bit.png", cv2.IMREAD_UNCHANGED)
    heif_file = pillow_heif.from_bytes(
        mode="BGRA;16",
        size=(cv_img.shape[1], cv_img.shape[0]),
        data=bytes(cv_img)
    )

Enumerating images
------------------

.. code-block:: python

    print("number of images in file:", len(heif_file))
    for img in heif_file:
        print(img)

.. note:: ``HeifFile`` itself points to the primary image in the container.

Adding images
-------------

Add all images from second file:

.. code-block:: python

    heif_file_to_add = pillow_heif.open_heif("file2.heif")
    heif_file.add_from_heif(heif_file_to_add)

Add only first image from second file:

.. code-block:: python

    heif_file_to_add = pillow_heif.open_heif("file2.heif")
    heif_file.add_from_heif(heif_file_to_add[0])

Add image from Pillow:

.. code-block:: python

    heif_file.add_from_pillow(Image.open("file2.jpg"))

Add image from bytes:

.. code-block:: python

    heif_file.add_frombytes(
            mode="BGRA",    # depends on image in `cv_img`
            size=(cv_img.shape[1], cv_img.shape[0]),
            data=bytes(cv_img)
        )

Removing images
---------------

Remove image at position with index ``0``:

.. code-block:: python

    del heif_file[0]

Swap image positions
--------------------

Starting from version `0.3.1` all images are in public list, and you can swap them as usual list elements.

.. code-block:: python

    heif_file.images[0], heif_file.images[1] = heif_file.images[1], heif_file.images[0]

Saving images
-------------

Refer to :py:meth:`~pillow_heif.HeifFile.save` to see what additional parameters is supported and to :ref:`encoding`.

.. code-block:: python

    heif_file.save("output.heif", quality=-1)

.. _image_data:

Accessing image data
--------------------

Decoded image data from ``libheif`` available throw :py:attr:`~pillow_heif.HeifImage.data` property
with the help of :py:attr:`~pillow_heif.HeifImage.stride` property.

Accessing `Primary` image in a file:

.. code-block:: python

    print(len(heif_file.data), heif_file.stride)

Or you can access each image by index:

.. code-block:: python

    print(len(heif_file[0].data), heif_file[0].stride)

.. note:: Actual size of data returned by ``data`` can be bigger then ``width * height * pixel size``.
    Use Numpy array to get decoded data without libheif ``padding`` at each row at the end.

Numpy array interface
---------------------

Next code gets decoded primary image data as a numpy array(in the same format as ``Pillow`` does):

.. code-block:: python

    heif_file = pillow_heif.open_heif("file.heif")
    np_array = np.asarray(heif_file)

Accessing image by index(for multi-frame images):

.. code-block:: python

    heif_file = pillow_heif.open_heif("file.heif")
    np_array = np.asarray(heif_file[0])     # accessing image by index.

After that you can load it at any library that supports numpy arrays.

.. note:: You can use ``convert_to`` before getting a numpy array to get it in other format.
