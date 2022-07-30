"""
Import this file to auto register an AVIF plugin for Pillow.
"""

from .as_opener import register_avif_opener

register_avif_opener()
