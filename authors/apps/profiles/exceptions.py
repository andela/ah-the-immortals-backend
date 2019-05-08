from rest_framework.exceptions import APIException


class UserNotFound(APIException):
    """exception message"""
    status_code = 404
    default_detail = 'User with that username Not found'
