import json
from collections import OrderedDict

from authors.apps.articles.models import Tag
from authors.utils.baseserializer import BaseSerializer
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .exceptions import ArticleNotFound
from .models import Article, Comment, Favorite, RatingModel


class ArticleSerializer(BaseSerializer):
    """
    Articles serializer
    """

    def __init__(self, *args, **kwargs):
        super(ArticleSerializer, self).__init__(*args, **kwargs)

    author = serializers.ReadOnlyField(source="get_author_details")
    like_info = serializers.SerializerMethodField()
    favorites = serializers.SerializerMethodField()

    def get_user_article(self):
        request = self.context.get('request', None)
        slug = self.context.get('article', None)

        if request.user.is_anonymous:
            return ((False, None))

        user = request.user.id
        article = Article.objects.get(slug=slug).id

        return (user, article)

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

    def get_likes_count(self, obj):
        article = self.get_likes_data()
        return article.votes.count()

    def get_dislikes_count(self, obj):
        article = self.get_likes_data()
        return article.votes.count(1)

    def get_favorite(self, instance):
        user, article = self.get_user_article()
        is_favorited = Favorite().is_favorited(user, article)
        return is_favorited

    def get_like_info(self, obj):
        mapped_data = {
            "like": self.get_like(self),
            "dislike": self.get_dislike(self),
            "likeCount": self.get_likes_count(self),
            "dislikeCount": self.get_dislikes_count(self)
        }

        return mapped_data

    def get_favorites(self, obj):
        mapped_data = {
            "favorite": self.get_favorite(self),
            "favoritesCount": obj.favoritesCount,
        }

        return mapped_data

    def get_ratings(self, obj):
        article = self.get_likes_data()
        request = self.context.get('request', None)
        ratings = RatingModel().ratings(article.id, request.user.id)
        return ratings

    ratings = serializers.SerializerMethodField()
    image_url = serializers.ReadOnlyField(source='get_image')

    class Meta:
        model = Article
        fields = (
            'slug', 'title', 'description', 'body', 'image', 'image_url',
            'created_at', 'updated_at', 'author', 'ratings', 'tagList',
            'like_info', 'comments', 'favorites', 'readtime'
        )
        extra_kwargs = {
            'image': {'write_only': True, 'required': False}
        }


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
        return OrderedDict([
            ("pageCount", len(self.page.object_list)),
            ('articlesCount', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])


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


class DisplayCommentsSerializer(serializers.ModelSerializer):
    """
    Serializer for rendering comments
    """
    class Meta:
        model = Article
        fields = ("comments",)


class DisplaySingleComment(serializers.ModelSerializer):
    """
    Serializes single representation of any comment
    """
    class Meta:
        model = Comment
        fields = ("representation",)


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
