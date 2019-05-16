from rest_framework.exceptions import APIException


class FieldNotSupported(APIException):
    """
    Exception for an unsupported field
    """
    status_code = 404
    default_detail = "Field must be; title, body or description"


class StartIndexError(APIException):
    """
    Exception for Start index greater than End index
    """
    status_code = 400
    default_detail = "Start index cannot be greater than End index"


class IndexOutOfRange(APIException):
    """
    Exception for Index beyond String length
    """
    status_code = 400
    default_detail = "start or end index cannot be greater than field length"


class NotPermittedError(APIException):
    """
    Exception for no permission to perform an action
    """
    status_code = 400
    default_detail = "You cannot delete or update highlight that is not yours"


class HighlightNotFound(APIException):
    """
    Exception for Highlight does not exist
    """
    status_code = 404
    default_detail = "Highlight removed or does not exist"


class UpdateFieldError(APIException):
    """
    Exception for Update field error
    """
    status_code = 400
    default_detail = "You cannot update the field"


class InvalidIndexError(APIException):
    """
    Exception for Index below zero
    """
    status_code = 400
    default_detail = "Start index or end index cannot be a negative number"
