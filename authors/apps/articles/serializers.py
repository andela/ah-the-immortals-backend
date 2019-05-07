from rest_framework import serializers
from .models import Article
import json
from authors.apps.articles.models import Tag


class ArticleSerializer(serializers.ModelSerializer):
    """
    Articles serializer
    """
    author = serializers.ReadOnlyField(source="get_author_details")

    class Meta:
        model = Article
        fields = (
            'slug', 'title', 'description', 'body', 'created_at',
            'updated_at', 'author', 'tagList'
        )


def add_tag_list(tag_names, article):
    """
    Adds tag list to an article
    """
    for name in tag_names:
        if name:
            tag, created = Tag.objects.get_or_create(
                tag_name=name
            )
            article.tags.add(tag)
