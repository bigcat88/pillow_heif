Workarounds
===========

Exif/XMP Orientation Tag
------------------------

Q. What is Exif Orientation Tag
"""""""""""""""""""""""""""""""

The Exif specification defines an Orientation Tag to indicate the orientation of the camera relative
to the captured scene. This can be used by the camera either to indicate the orientation automatically
by an orientation sensor, or to allow the user to indicate the orientation manually by a menu switch,
without actually transforming the image data itself.

Q. So what's the problem?
"""""""""""""""""""""""""

Excerpt from HEIF standard:

*Metadata specified in Annex A or according to the item type and MIME type values is descriptive and
does not normatively affect the presentation. In particular, an image item can be rotated by 90°, 180°,
or 270° using the 'irot ' transformative item property. Rotation metadata, e.g. according to Annex A,
is ignored in the displaying process.*

So EXIF metadata is informational only, if we do all by standard.

But some apps in macOS(for example built-in ``Preview``), do rotation based on Exif TAG.

And their behaviour is very weird, if there is one image in heif file with orientation, they perform rotation,
but if there are two images and second does not have exif orientation tag, they did not do even for first image.

`Discussion in libheif repository <https://github.com/strukturag/libheif/issues/227>`_

As we do not have an own soothsayer to say in which image editor will be image opened and
will app rotate image or not based on Exif TAG, we comes to next chapter...

*Updated(October 2023): last macOS Sonoma(14.0) changed it's behaviour and do not rotate `HEIF` images based on Exif TAG.*

Q. So is there a decision?
""""""""""""""""""""""""""

The best one and simplest solution is to
`remove it <https://github.com/strukturag/libheif/issues/219#issuecomment-638110043>`_.

So we set ``orientation`` to ``1`` in
:py:meth:`~pillow_heif.HeifFile.add_from_pillow` to remove EXIF/XMP orientation tag
and rotate the image according to the removed tag.

.. note:: *Updated(November 2023, pillow_heif>=1.14.0, PillowPlugin mode):
    Image rotation value during encoding will be not removed from EXIF, and in addition will be set in HEIF header.*

That allow us to properly handle situations when JPEG or PNG with orientation get encoded to HEIF.

To properly handle HEIF images with rotation tag in Exif/XMP, in Pillow plugin we do the same during image open,
by calling :py:func:`~pillow_heif.set_orientation` function.

.. note:: When using :py:func:`~pillow_heif.open_heif` and :py:meth:`~pillow_heif.HeifFile.add_from_heif` functions
    orientation tag will not be get reset automatically.

Here is list of functions and method that resets orientations automatically:
    * :py:func:`pillow_heif.from_pillow`
    * :py:meth:`pillow_heif.HeifFile.add_from_pillow`
    * :py:meth:`pillow_heif.HeifImage.to_pillow`
    * :py:class:`pillow_heif.HeifImageFile` *Pillow plugin class*
    * :py:class:`pillow_heif.AvifImageFile` *Pillow plugin class*
