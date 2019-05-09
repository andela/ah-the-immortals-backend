from rest_framework import serializers
from .models import Article
import json


class ArticleSerializer(serializers.ModelSerializer):
    """
    Articles serializer
    """
    author = serializers.ReadOnlyField(source="get_author_details")

    class Meta:
        model = Article
        fields = (
            'slug', 'title', 'description', 'body', 'created_at',
            'updated_at', 'author'
        )
