"""
Custom exceptions for API operations
"""


class IdentifierFormatError(ValueError):
    """
    Custom exception for validation fail on UUID string parameters
    """
    def __init__(self, identifier):
        message = ("{} parameters must be correctly "
                   "formatted UUID strings".format(identifier))
        super().__init__(message)


class AuthorizationError(Exception):
    """
    Custom exception for failed authorization
    """
    def __init__(self):
        message = "Key not authorized to perform this action"
        super().__init__(message)


class FileTypeError(Exception):
    """
    Custom exception for inappropriate CNV file types
    """
    def __init__(self, filetype):
        message = ("CNV file must be of type .tsv or .txt "
                   "not {}".format(filetype))
        super().__init__(message)


class KeyExistenceError(Exception):
    """
    Custom exception for missing Patient or Sample IDs
    """
    def __init__(self, key):
        message = ("Missing {} when attempting to add CNV file"
                   .format(key))
        super().__init__(message)


class HeaderError(Exception):
    """
    Custom exception for missing headers in CNV file
    """
    def __init__(self, required):
        message = ("Headers in provided CNV file do not match "
                   "required headers: {}".format(required))
        super().__init__(message)
