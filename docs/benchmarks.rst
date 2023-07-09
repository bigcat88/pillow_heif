Benchmarks
==========

Decode benchmarks
-----------------

Images info:

pug.heic - 4032x3024 = 12MP, photo taken on iPhone with all metadata.

cat.hif - 2832x4240 = 12MP, 10 bit image, with Exif and IPTC data.

image_large.heic - 6000x8000 = 48MP, with Exif and IPTC data.

Pillow load
^^^^^^^^^^^

.. image:: ../benchmarks/results_decode_pillow_load_Windows.png

.. image:: ../benchmarks/results_decode_pillow_load_Linux.png

.. image:: ../benchmarks/results_decode_pillow_load_macOS.png

Numpy BGR
^^^^^^^^^

.. image:: ../benchmarks/results_decode_numpy_bgr_Windows.png

.. image:: ../benchmarks/results_decode_numpy_bgr_Linux.png

.. image:: ../benchmarks/results_decode_numpy_bgr_macOS.png

Numpy RGB
^^^^^^^^^

.. image:: ../benchmarks/results_decode_numpy_rgb_Linux.png

.. image:: ../benchmarks/results_decode_numpy_rgb_Windows.png

.. image:: ../benchmarks/results_decode_numpy_rgb_macOS.png

Encode benchmarks
-----------------

All images with size 4096x4096 = 16MP, without exif, xmp or other data, except `pug.heic`.

.. image:: ../benchmarks/results_encode_Windows.png

.. image:: ../benchmarks/results_encode_Linux.png

.. image:: ../benchmarks/results_encode_macOS.png
