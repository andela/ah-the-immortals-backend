from rest_framework import serializers
from .models import Highlight


class HighlightSerializer(serializers.ModelSerializer):
    """
    Highlights serializer
    """
    highlighted_by = serializers.ReadOnlyField(source="user_details")
    article_slug = serializers.ReadOnlyField(source="article_details")
    highlighted_text = serializers.ReadOnlyField(source="get_highlighted_text")

    class Meta:
        model = Highlight
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'article', 'field',
                        'start_index', 'end_index'),
                message=("You have already highlighted this section")
            )
        ]
        fields = (
            'user', 'id', 'article', 'article_slug', 'field', 'comment',
            'start_index', 'end_index', 'highlighted_text', 'highlighted_by'
        )
        extra_kwargs = {
            'user': {'write_only': True},
            'article': {'write_only': True}
        }
