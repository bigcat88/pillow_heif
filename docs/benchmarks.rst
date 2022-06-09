Decoding Benchmarks
===================

Tests performed on Intel CPU i7-9700.

.. code-block:: python

    DATASET = [Path("etc_heif/arrow.heic"), Path("etc_heif/nokia/alpha_3_2.heic"), Path("etc_heif/cat.hif")]

Benchmark code A
----------------

.. code-block:: python

    def open_heif_file():
        for image_path in DATASET:
            heif_file = open_heif(image_path)
            for image in heif_file:
                assert image.size[0] > 0
                assert image.bit_depth >= 8
                assert image.mode == "RGBA" if image.has_alpha else "RGB"
                for thumb in image.thumbnails:
                    assert thumb.size[0] > 0
                    assert thumb.bit_depth >= 8
                    assert thumb.mode == "RGBA" if thumb.has_alpha else "RGB"

    benchmark.pedantic(open_heif_file, iterations=2, rounds=30, warmup_rounds=1)

Benchmark code B
----------------

.. code-block:: python

    def load_thumbnails():
        for image_path in DATASET:
            heif_file = open_heif(image_path, convert_hdr_to_8bit=False)
            assert len(list(heif_file.thumbnails_all()))
            for thumbnail in heif_file.thumbnails_all():
                assert thumbnail.data

    benchmark.pedantic(load_thumbnails, iterations=2, rounds=30, warmup_rounds=1)

Benchmark code C
----------------

.. code-block:: python

    def load_image():
        for image_path in DATASET:
            heif_file = open_heif(image_path, convert_hdr_to_8bit=False)
            for image in heif_file:
                assert image.data

    benchmark.pedantic(load_image, iterations=1, rounds=30, warmup_rounds=1)

Results
-------

+-------------------------------+--------------+----------------+
| Benchmark                     | CPython 3.10 | PyPy 3.8 7.3.9 |
+===============================+==============+================+
| open_heif_file ver<0.2.4      | 58 ms        | 52 ms          |
+-------------------------------+--------------+----------------+
| open_heif_file mem_ctx=False  | 49 ms        | 45 ms          |
+-------------------------------+--------------+----------------+
| open_heif_file mem_ctx=True   | **15 ms**    | **18 ms**      |
+-------------------------------+--------------+----------------+
| load_thumbnails ver<0.2.4     | 155 ms       | 150 ms         |
+-------------------------------+--------------+----------------+
| load_thumbnails mem_ctx=False | 149 ms       | 143 ms         |
+-------------------------------+--------------+----------------+
| load_thumbnails mem_ctx=True  | **114 ms**   | **115 ms**     |
+-------------------------------+--------------+----------------+
| load_image ver<0.2.4          | 813 ms       | 813 ms         |
+-------------------------------+--------------+----------------+
| load_image mem_ctx=False      | 808 ms       | 806 ms         |
+-------------------------------+--------------+----------------+
| load_image mem_ctx=True       | **763 ms**   | **767 ms**     |
+-------------------------------+--------------+----------------+

Reference: :py:attr:`~pillow_heif._options.PyLibHeifOptions.ctx_in_memory`

Conclusion
----------

After optimizations it became faster from 1% to 17%, depending on operations types.
If you only decode main image you barely notice this changes,
but if you first opens and looks at image properties, metadata the new version is faster.

Moving to ``ctx_mem`` = ``True`` what is by default now, gives much more significant boost even on decoding.
Reading HEIF metadata and image properties gives us ``3x`` faster speed.
Decoding of small images, what we test here by decoding thumbnails, gives us ``30%`` increase of speed.
Decoding of big images becomes faster by 5%, after we switch to ``ctx_mem`` = ``True``.

Encoding benchmarks
===================

Comparing 0.2.5 and 0.3.0 on CPython 3.10

.. code-block:: python

    DATASET = [Path("rgb8_512_512_1_2.heic"), Path("etc_heif/nokia/alpha_3_2.heic"), Path("rgb10_639_480_1_3.heic")]

Benchmark code A
----------------

.. code-block:: python

    def save_heif_file():
        out_buf = BytesIO()
        for image_path in DATASET:
            heif_file = open_heif(image_path)
            heif_file.save(out_buf)

    benchmark.pedantic(save_heif_file, iterations=1, rounds=40, warmup_rounds=1)

Benchmark code B
----------------

.. code-block:: python

    def pillow_save_heif():
        out_buf = BytesIO()
        for image_path in DATASET:
            image = Image.open(image_path)
            image.save(out_buf, save_all=True, format="HEIF")

    benchmark.pedantic(pillow_save_heif, iterations=1, rounds=40, warmup_rounds=1)

+-------------------------------+----------+----------+
| Benchmark                     |   0.2.5  |   0.3.0  |
+===============================+==========+==========+
| **A** `HeiFile` mem_ctx=False |  1.81 s  |  1.79 s  |
+-------------------------------+----------+----------+
| **A** `HeiFile` mem_ctx=True  |  1.80 s  |  1.78 s  |
+-------------------------------+----------+----------+
| **B** `Pillow` mem_ctx=False  |  1.92 s  |  1.90 s  |
+-------------------------------+----------+----------+
| **B** `Pillow` mem_ctx=True   |  1.91 s  |  1.89 s  |
+-------------------------------+----------+----------+
