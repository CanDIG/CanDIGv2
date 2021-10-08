"""
Custom exceptions for API operations
"""


class IdentifierFormatError(ValueError):
    """
    Custom exception for validation fail on UUID string parameters
    """
    def __init__(self, identifier):
        message = "{} parameters must be correctly formatted UUID strings".format(identifier)
        super().__init__(message)


class AuthorizationError(Exception):
    """
    Custom exception for failed authorization
    """
    def __init__(self):
        message = "Key not authorized to perform this action"
        super().__init__(message)
