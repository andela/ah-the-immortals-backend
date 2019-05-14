from authors.apps.articles.models import Article
from .serializers import EscalationSerializer
from .exceptions import ArticleNotFound
from django.shortcuts import render

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.exceptions import ValidationError

from .models import EscalationModel


def fetch_an_article(slug):
    """
    Gets an article from the database
    """
    try:
        article = Article.objects.get(slug=slug)
        return article
    except Article.DoesNotExist:
        raise ArticleNotFound


class ExcalationAPIView(GenericAPIView):
    """
    User can report an article
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = EscalationSerializer

    def post(self, request, slug):
        """
        Creates a single report for a specific article
        """

        article = fetch_an_article(slug)
        report = request.data

        if article.author == request.user:
            raise ValidationError(
                detail={
                    "error": "You can't report your article."
                }
            )
        try:
            already_reported = EscalationModel.objects.get(
                article=article,
                reporter=request.user,
                reason=report['reason']
            )
            if already_reported.description == report['description']:
                return Response({
                    "error": "You are not allowed to report twice"
                }, status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(already_reported, data=report)
        except EscalationModel.DoesNotExist:
            serializer = self.serializer_class(data=report)
        serializer.is_valid(raise_exception=True)
        serializer.save(article=article, reporter=request.user)
        articles = {
            "artcile": {
                "slug": serializer.data['article']['slug'],
                "title": serializer.data['article']['title'],
                "description": serializer.data['article']['description'],
                "body": serializer.data['article']['body'],
                "created_at": serializer.data['article']['created_at'],
                "updated_at": serializer.data['article']['updated_at']
            }}

        articles.update({'report': {
            "reason": serializer.data.get('reason'),
            "description": serializer.data.get('description')
        }})
        articles.update({
            'message': "You have succesfully reported an "
            + "article ({})".format(serializer.data['article']['title'])})

        return Response(articles, status=status.HTTP_201_CREATED)

    def delete(self, request, slug):
        """
        Admin to delete an article
        """

        article = fetch_an_article(slug)
        user = request.user

        if user.is_staff:
            article.delete()
        else:
            return Response({
                "error": "Only Admins can delete a reported article"
            },
                status.HTTP_403_FORBIDDEN)
        return Response({
            "message": "You successfully deleted the article"
        },
            status.HTTP_200_OK)


class FetchExcalationAPIView(GenericAPIView):
    """
    User can report an article
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = EscalationSerializer

    def get(self, request):
        """
        Admin can get a reported articles
        """

        user = request.user

        if user.is_staff:
            all_articles = EscalationModel.objects.all()
            articles = []
            for art in all_articles:
                serializer = EscalationSerializer(art)
                articles.append(serializer.data)

            return Response(
                data={"escalated articles": articles},
                status=status.HTTP_200_OK
            )
        else:
            return Response({
                "error": "Only Admins can get reported article"
            },
                status.HTTP_403_FORBIDDEN)
