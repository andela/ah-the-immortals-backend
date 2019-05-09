from rest_framework.exceptions import APIException


class ItemDoesNotExist(APIException):
    status_code = 404
    default_detail = "Comment or the Article was not found"


class ArticleNotFound(APIException):
    """exception message"""
    status_code = 404
    default_detail = 'Article does not exist'


class Forbidden(APIException):
    status_code = 403
    default_detail = 'You cannot edit or delete a comment you dont own'
