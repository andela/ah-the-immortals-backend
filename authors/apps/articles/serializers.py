from rest_framework import serializers
from .models import Article
import json


class ArticleSerializer(serializers.ModelSerializer):
    """
    Articles serializer
    """
    image_url = serializers.ReadOnlyField(source="get_image")
    # author = serializers.ReadOnlyField(source="get_authors")

    class Meta:
        model = Article
        fields = (
            'slug', 'title', 'description', 'body', 'created_at',
            'updated_at', 'author', 'image_url'
        )
