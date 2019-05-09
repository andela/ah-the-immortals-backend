from .serializers import (
    ArticleSerializer, CommentDetailSerializer, CommentSerializer, CommentChildSerializer)
from .models import Article, Comment
from .exceptions import ArticleNotFound, Forbidden, ItemDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.exceptions import APIException
from rest_framework.generics import ListCreateAPIView, GenericAPIView
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)


class ListCreateArticleAPIView(ListCreateAPIView):
    """
    Create Article
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer

    def create(self, request):
        """
        Create an article
        """
        article = request.data
        article["author"] = request.user.pk
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response({"article": serializer.data},
                        status=status.HTTP_201_CREATED)

    def get(self, request):
        """
        Get all articles
        """
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response({"articles": serializer.data,
                         "articlesCount": len(serializer.data)},
                        status=status.HTTP_200_OK)


class RetrieveUpdateArticleAPIView(GenericAPIView):
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
            raise ArticleNotFound

    def get(self, request, slug):
        """
        Get one article
        """
        article = self.retrieve_article(slug)
        if article:
            serializer = ArticleSerializer(article, many=False)
            return Response({"article": serializer.data},
                            status=status.HTTP_200_OK)

    def patch(self, request, slug):
        """
        Update an article
        """
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise ArticleNotFound
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
                status.HTTP_403_FORBIDDEN)

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
                    "Cannot delete an article that is not yours"
                ]}},
                status.HTTP_403_FORBIDDEN)
        return Response({"message": "Article deleted"},
                        status.HTTP_200_OK)


class CommentAPIView(GenericAPIView):
    """
    class for post and get comments
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def post(self, request, **kwargs):
        """
        post a comment on an article 
        """
        comment = request.data.get('comment', {})
        try:
            slug = self.kwargs['slug']
            article = Article.objects.get(slug=slug)

            author = request.user
            comment['author'] = author.id
            comment['article'] = article.id
            serializer = self.serializer_class(data=comment)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Article.DoesNotExist:
            raise ArticleNotFound

    def get(self, request, slug):
        """
         Get multiple comments
        """
        self.serializer_class = CommentChildSerializer
        try:
            article = Article.objects.get(slug=slug)
            article_id = article.id
            comment = Comment.objects.all().filter(article_id=article_id)
            serializer = self.serializer_class(comment, many=True)
            return Response({'comments': serializer.data}, status.HTTP_200_OK)
        except Article.DoesNotExist:
            raise ItemDoesNotExist


class CommentDetailAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = CommentDetailSerializer

    def get(self, request, slug, id):
        """
        get a comment
        """

        comment = Comment.objects.all().filter(id=id)
        serializer = self.serializer_class(comment, many=True)
        return Response({"comment": serializer.data}, status.HTTP_200_OK)

    def post(self, request, slug, id):
        """
        create a comment
        """
        comment = request.data.get('reply')
        article = get_object_or_404(Article, slug=slug)
        author = request.user
        comment['author'] = author.id
        comment['article'] = article.id
        comment['parent'] = id
        serializer = self.serializer_class(data=comment)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """ 
        update a comment
        """
        comment = request.data.get('comment', {})
        try:
            Id = kwargs['id']
            slug = kwargs['slug']
            comment_obj = Comment.objects.get(pk=Id)
            article = get_object_or_404(Article, slug=slug)
            if comment_obj.author == request.user:
                comment['author'] = request.user.id
                comment['article'] = article.id
                serializer = self.serializer_class(comment_obj, data=comment)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            else:
                raise Forbidden
        except Comment.DoesNotExist:
            return Response(
                {
                    "error": {
                        "body": ["unsuccesful update either the comment or"
                                 "slug not found"
                                 ]}},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, **kwargs):
        """
        delete a comment 
        """
        try:
            comment_obj = Comment.objects.get(id=kwargs['id'])
            if request.user == comment_obj.author:
                comment_obj.delete()
                return Response({
                    "message": {
                        "body": ["Comment deleted successfully"]}},
                    status=status.HTTP_200_OK)
            else:
                raise Forbidden
        except Comment.DoesNotExist:
            raise ItemDoesNotExist
