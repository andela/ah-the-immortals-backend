from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework import status, exceptions
from .models import Article, Comment
from ..profiles.models import Profile
import json
User = get_user_model()


class ArticleSerializer(serializers.ModelSerializer):
    """
    Articles serializer
    """
    image_url = serializers.ReadOnlyField(source="get_image")
    author = serializers.ReadOnlyField(source="get_author_details")

    class Meta:
        model = Article
        fields = (
            'slug', 'title', 'description', 'body', 'created_at',
            'updated_at', 'author', 'image_url'
        )


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_at',
                  'article', 'author', 'parent')


class CommentChildSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="get_profile_details")

    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_at', 'author', 'parent')


class CommentDetailSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'body', 'article',
                  'created_at', 'replies', 'parent')

    @staticmethod
    def get_replies(obj):
        if obj.is_parent:
            return CommentChildSerializer(obj.children(), many=True).data
        return None
