from rest_framework import serializers
from .models import Article, Favorite
import json
from authors.apps.articles.models import Tag
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from rest_framework.response import Response
from .exceptions import ArticleNotFound
from authors.apps.utils.baseserializer import BaseSerializer


class ArticleSerializer(BaseSerializer):
    """
    Articles serializer
    """

    def __init__(self, *args, **kwargs):
        super(ArticleSerializer, self).__init__(*args, **kwargs)

    author = serializers.ReadOnlyField(source="get_author_details")

    def get_likes_data(self):
        article = self.instance
        return article

    def get_likes(self, vote):
        article = self.get_likes_data()
        request = self.context.get('request', None)
        votetf = article.votes.exists(request.user.id, vote)
        return votetf

    def get_like(self, obj):
        like = self.get_likes(0)
        return like

    def get_dislike(self, obj):
        like = self.get_likes(1)
        return like

    def get_likesCount(self, obj):
        article = self.get_likes_data()
        like_count = article.num_vote_up
        return like_count

    def get_dislikesCount(self, obj):
        article = self.get_likes_data()
        dislike_count = article.num_vote_down
        return dislike_count

    like = serializers.SerializerMethodField()
    dislike = serializers.SerializerMethodField()
    likesCount = serializers.SerializerMethodField()
    dislikesCount = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'slug', 'title', 'description', 'body', 'created_at',
            'updated_at', 'author', 'tagList', 'like', 'dislike',
            'likesCount', 'dislikesCount'
        )


def add_tag_list(tag_names, article):
    """
    Adds tag list to an article
    """
    for name in tag_names:
        if name.strip():
            tag, created = Tag.objects.get_or_create(
                tag_name=name.strip()
            )
            article.tags.add(tag)


class ArticlePaginator(PageNumberPagination):
    """
    Custom pagination for Articles
    """

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('articlesCount', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class FavoritedArticlesSerializer(serializers.ModelSerializer):
    """
    A class to fetch all favorited articles
    """
    favorited = serializers.ReadOnlyField(source="get_favorited")
    author = serializers.ReadOnlyField(source="get_author_details")

    class Meta:
        model = Article
        fields = (
            'slug', 'title', 'description', 'body',
            'created_at', 'favorited', 'favoritesCount',
            'updated_at', 'author'
        )


class FavoritesSerializer(serializers.ModelSerializer):
    """
    A class to serialize favorite article and user
    """
    class Meta:
        model = Favorite
        fields = (
            'user', 'article'
        )
