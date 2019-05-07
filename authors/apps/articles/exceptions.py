from rest_framework.exceptions import APIException


class ArticleNotFound(APIException):
    """exception message"""
    status_code = 404
    default_detail = 'Article does not exist'
