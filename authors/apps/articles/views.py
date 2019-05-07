from django.shortcuts import render
from rest_framework.exceptions import APIException
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from .models import Article
from .serializers import ArticleSerializer


class ListCreateArticleAPIView(ListCreateAPIView):
    """
    Create Articles CRUD
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer

    def create(self, request):
        article = request.data.get("article", {})
        article["author"] = request.user.pk
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response({"articles": serializer.data,
                        "articlesCount": len(serializer.data)},
                        status=status.HTTP_200_OK)


class RetrieveUpdateArticleAPIView(APIView):
    """
    Retrive, Update and Delete an article
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer

    def retrieve_article(self, slug):
        """
        Fetch one article
        """
        try:
            article = Article.objects.get(slug=slug)
            return article
        except Article.DoesNotExist:
            return Response({"errors": {"error": ["Article does not exist"]}},
                            status.HTTP_404_NOT_FOUND)

    def get(self, request, slug):
        """
        Get article by slug
        """
        article = self.retrieve_article(slug)
        if article:
            serializer = ArticleSerializer(article, many=False)
            return Response({"article": serializer.data},
                            status=status.HTTP_200_OK)

    def patch(self, request, slug):
        """
        Update article
        """
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({"errors": {"error": ["Article does not exist"]}},
                            status.HTTP_404_NOT_FOUND)
        user = request.user
        if article.author == user:
            serializer = ArticleSerializer(
                instance=article,
                data=request.data,
                partial=True
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"article": serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": {
                                "error": [
                                    "Cannot edit an article that is not yours"
                                    ]}},
                            status.HTTP_404_NOT_FOUND)

    def delete(self, request, slug):
        """
        Delete an article
        """
        article = self.retrieve_article(slug)
        user = request.user
        if article.author == user:
            article.delete()
        else:
            return Response({"errors": {
                                "error": [
                                    "Cannot edit an article that is not yours"
                                    ]}},
                            status.HTTP_403_FORBIDDEN)
        return Response({"message": "Article deleted"},
                        status.HTTP_200_OK)
