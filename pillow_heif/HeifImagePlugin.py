"""
Import this file to auto register a HEIF plugin for Pillow.
"""

from .as_opener import register_heif_opener

register_heif_opener()
