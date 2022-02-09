"""
Exceptions that can be raised during library calls.
"""


class HeifError(Exception):
    def __init__(self, *, code, subcode, message):
        super().__init__(code, subcode, message)
        self.code = code
        self.subcode = subcode
        self.message = message

    def __str__(self):
        return f'Code: {self.code}, Subcode: {self.subcode}, Message: "{self.message}"'

    def __repr__(self):
        return f'HeifError({self.code}, {self.subcode}, "{self.message}"'
