from django_filters import rest_framework as filters
# from rest_framework.generics import ListAPIView
from .serializers import ArticleSerializer
from authors.apps.articles.models import Article
from rest_framework.response import Response
from rest_framework import status
# from rest_framework.filters import SearchFilter


class ArticleFilter(filters.FilterSet):
    """
    class handling the filtering of articles:
        filter-params:
        - author
        - title
        - Tags
    returns article depending on the supplied param
    """
    author = filters.CharFilter(field_name='author__username',
                                lookup_expr='icontains'
                                )
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')

    tags = filters.CharFilter(field_name='tags',
                              method='get_tags',
                              lookup_expr='iexact'
                              )

    class Meta:
        model = Article
        fields = ['author', 'title', 'tags']

    def get_tags(self, queryset, tags, value):
        # remove all spaces and create a list by spliting where there
        # # is a comma
        valueList = value.replace(" ", "").split(',')
        return queryset.filter(tags__tag_name__in=valueList).distinct()
