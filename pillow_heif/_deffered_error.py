"""
DeferredError class taken from PIL._util.py file.
"""


class DeferredError:  # pylint: disable=too-few-public-methods
    """Allow failing import for doc purposes, as C module will be not build at `.readthedocs`"""

    def __init__(self, ex):
        self.ex = ex

    def __getattr__(self, elt):
        raise self.ex
