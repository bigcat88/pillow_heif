class HeifError(Exception):
    def __init__(self, *, code, subcode, message):
        self.code = code
        self.subcode = subcode
        self.message = message

    def __str__(self):
        return f'Code: {self.code}, Subcode: {self.subcode}, Message: "{self.message}"'

    def __repr__(self):
        return f'HeifError({self.code}, {self.subcode}, "{self.message}"'
