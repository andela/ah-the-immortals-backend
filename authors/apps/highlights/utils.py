from .exceptions import (FieldNotSupported, StartIndexError,
                         IndexOutOfRange, UpdateFieldError,
                         InvalidIndexError)


def validate_field(article_field):
    field_list = ["title", "description", "body"]
    if article_field not in field_list:
        raise FieldNotSupported


def validate_index(field_data, index_start, index_end):
    string_size = len(field_data)
    if index_start < 0 or index_end < 0:
        raise InvalidIndexError
    if index_start > index_end:
        raise StartIndexError
    if index_end > string_size:
        raise IndexOutOfRange


def check_field(article, article_field):
    if article_field == "title":
        field_data = article.title
    elif article_field == "description":
        field_data = article.description
    elif article_field == "body":
        field_data = article.body
    return field_data


def retrieve_word(field_data, start_index, end_index):
    character_set = field_data[start_index:end_index+1]
    return character_set


def validate_update_field(field):
    if field:
        raise UpdateFieldError


def valid_index(index, field_data):
    if index < 0:
        raise InvalidIndexError
    if index > len(field_data):
        raise IndexOutOfRange
