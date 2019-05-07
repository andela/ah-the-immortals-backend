import json
from collections import OrderedDict

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from authors.apps.articles.models import Tag
from authors.utils.baseserializer import BaseSerializer

from .exceptions import ArticleNotFound
from .models import Article, Comment, Favorite, RatingModel


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


class RatingSerializer(ArticleSerializer):
    """
    Serializer class to rate an article
    """

    rated_by = serializers.ReadOnlyField()
    article = serializers.ReadOnlyField(source='get_articles_details')
    rate = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=True
    )
    average_rating = serializers.SerializerMethodField(
        method_name="calulate_average_rating"
    )

    class Meta:
        model = RatingModel
        fields = ('rate',
                  'average_rating',
                  'article',
                  'rated_by'
                  )

    def calulate_average_rating(self, obj):
        """
        Calculate the average rating of an article
        """
        average_rate = RatingModel.objects.filter(article=obj.article,
                                                  ).aggregate(rate=Avg('rate'))

        if average_rate["rate"]:
            return float('%.2f' % (average_rate["rate"]))
        return 0


class CommentSerializer(serializers.ModelSerializer):
    """
    Comments serializer
    """
    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_at',
                  'article', 'author', 'parent')


class CommentChildSerializer(serializers.ModelSerializer):
    """
    child Comments serializer
    """
    author = serializers.ReadOnlyField(source="get_profile_details")

    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_at', 'author', 'parent')


class CommentDetailSerializer(serializers.ModelSerializer):
    """
    Comments with replies serializer
    """
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'body', 'article',
                  'created_at', 'replies', 'parent')

    @staticmethod
    def get_replies(obj):
        """
        utility function to get replies
        """
        if obj.is_parent:
            return CommentChildSerializer(obj.children(), many=True).data
        return None
