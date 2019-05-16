from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from .models import Highlight
from .serializers import HighlightSerializer
from .exceptions import NotPermittedError, HighlightNotFound
from .utils import (validate_field, validate_index, check_field,
                    retrieve_word, validate_update_field, valid_index)
from ..articles.views import RetrieveUpdateArticleAPIView

check_article = RetrieveUpdateArticleAPIView()


class HighlightAPIView(GenericAPIView):
    """
    Highlight and comment on text views
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = HighlightSerializer

    def post(self, request, slug):
        """
        Create a text Highlight
        """
        article = check_article.retrieve_article(slug)
        highlight_data = request.data
        article_field = highlight_data.get("field")
        index_start = highlight_data.get("start_index")
        index_end = highlight_data.get("end_index")
        validate_field(article_field)
        field_data = check_field(article, article_field)
        validate_index(field_data, index_start, index_end)
        highlight_data["user"] = request.user.pk
        highlight_data["article"] = article.pk
        serializer = self.serializer_class(data=highlight_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "highlight": serializer.data,
            "message": "You highlighted this section"
        }, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        """
        Fetch all highlighted text for a single article for user
        """
        article = check_article.retrieve_article(slug)
        highlights = Highlight.objects.all().filter(article_id=article.id,
                                                    user=request.user.id)
        serializer = self.serializer_class(highlights, many=True)
        return Response({
            "highlights": serializer.data},
            status=status.HTTP_200_OK)


class RetrieveUpdateHighlightAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = HighlightSerializer

    def retrieve_highlight(self, slug, highlight_id):
        """
        Retrieve highlight
        """
        article = check_article.retrieve_article(slug)
        try:
            highlight = Highlight.objects.get(article_id=article.id,
                                              id=highlight_id)
            return highlight
        except Highlight.DoesNotExist:
            raise HighlightNotFound

    def delete(self, request, slug, highlight_id):
        """
        Remove a text highlight and comment
        """
        highlight = self.retrieve_highlight(slug, highlight_id)
        if request.user.id == highlight.user_id:
            highlight.delete()
            return Response({"message": "Highlight removed"},
                            status.HTTP_200_OK)
        raise NotPermittedError

    def patch(self, request, slug, highlight_id):
        """
        Update a highlight and comment
        """
        highlight = self.retrieve_highlight(slug, highlight_id)
        if request.user.id == highlight.user_id:
            field = request.data.get("field")
            validate_update_field(field)
            article = check_article.retrieve_article(slug)
            article_field = highlight.field
            field_data = check_field(article, article_field)
            index_start = request.data.get("start_index")
            index_end = request.data.get("end_index")
            if index_start:
                valid_index(index_start, field_data)
            if index_end:
                valid_index(index_end, field_data)
            serializer = self.serializer_class(
                instance=highlight,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            highlight = serializer.save()
            return Response({
                "highlight": serializer.data,
                "message": "Highlight updated successfully"
                    }, status.HTTP_200_OK)
        raise NotPermittedError
