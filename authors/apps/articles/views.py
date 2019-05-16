from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render
from django_filters import rest_framework as filters
from rest_framework import permissions, status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from ...utils.social_share_utils import generate_share_url
from .exceptions import ArticleNotFound, Forbidden, ItemDoesNotExist
from .filters import ArticleFilter
from .models import Article, Comment, Favorite, RatingModel, Tag
from .serializers import (ArticlePaginator, ArticleSerializer,
                          CommentChildSerializer, CommentDetailSerializer,
                          CommentSerializer,
                          DisplayCommentsSerializer,
                          DisplaySingleComment,
                          FavoritesSerializer,
                          RatingSerializer,
                          add_tag_list)


def get_serialiser_data(serializer_data, content):
    """
    Gets serializer information from content
    """
    response = None
    if serializer_data.data:
        data = serializer_data.data[0].get(content)
        if content == "comments":
            response = Response(
                data={
                    "comments": data
                },
                status=status.HTTP_200_OK
            )
        else:
            response = Response(
                data={
                    "comment": data
                },
                status=status.HTTP_200_OK
            )
    else:
        if content == "comments":
            response = Response(
                data={
                    "comments": "no comments on this article"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            response = Response(
                data={
                    "comments": "This article does not have a comment with"
                    " that id"
                },
                status=status.HTTP_404_NOT_FOUND
            )
    return response


class ListCreateArticleAPIView(ListCreateAPIView):
    """
    Create Article
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = ArticleFilter
    search_fields = ('title')

    def create(self, request):
        """
        Create an article
        """
        tag_names = request.data.get("tags")
        article = request.data
        article["author"] = request.user.pk
        serializer = self.serializer_class(
            data=article,
            remove_fields=['like_info', 'created_at', 'updated_at',
                           'favorites', 'ratings'])
        serializer.is_valid(raise_exception=True)
        article = serializer.save(author=request.user)
        data = serializer.data
        if tag_names:
            add_tag_list(tag_names, article)
        data["tagList"] = article.tagList
        return Response(
            data=data,
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        """
        Get all articles
        """
        page_limit = request.GET.get('page_limit')
        if not page_limit:
            page_limit = 10
        else:
            invalid_response = Response(
                data={
                    "detail": "Invalid page limit"
                },
                status=status.HTTP_404_NOT_FOUND
            )
            if not page_limit.isdigit():
                return invalid_response
            elif int(page_limit) < 1:
                return invalid_response
        articles = self.filter_queryset(self.get_queryset())
        paginator = ArticlePaginator()
        paginator.page_size = page_limit
        result = paginator.paginate_queryset(articles, request)
        serializer = ArticleSerializer(result, many=True,
                                       remove_fields=['like_info',
                                                      'comments',
                                                      'favorites',
                                                      'ratings'])
        response = paginator.get_paginated_response({
            "articles": serializer.data
        })
        if response.get("articlesCount") == 0:
            response["message"] = "We couldn’t find any articles"
        return Response(response)


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
            serializer = ArticleSerializer(
                article,
                context={'article': slug, 'request': request},
                many=False
            )
            return Response(
                {"article": serializer.data},
                status=status.HTTP_200_OK
            )

    def patch(self, request, slug):
        """
        Update an article
        """
        article = self.retrieve_article(slug)
        user = request.user
        if article.author == user:
            serializer = ArticleSerializer(
                instance=article,
                data=request.data,
                partial=True,
                remove_fields=['like_info', 'created_at', 'updated_at',
                               'favorites', 'ratings']
            )
            serializer.is_valid(raise_exception=True)
            article = serializer.save()
            data = serializer.data
            tag_names = request.data.get("tags")
            if tag_names:
                article.clear_tags()
                add_tag_list(tag_names, article)
            data["tagList"] = article.tagList
            return Response(
                data={
                    "article": data
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={
                    "errors": {
                        "error": [
                            "Cannot edit an article that is not yours"
                        ]
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )

    def delete(self, request, slug):
        """
        Delete an article
        """
        article = self.retrieve_article(slug)
        user = request.user
        if article.author == user:
            article.clear_tags()
            article.delete()
        else:
            return Response({"errors": {
                "error": [
                    "Cannot delete an article that is not yours"
                ]}},
                status.HTTP_403_FORBIDDEN)
        return Response({
            "message": "Article '{}' deleted".format(article.title)},
            status.HTTP_200_OK)


class FetchTags(GenericAPIView):
    """
    Fetchs all tags from database
    """

    def get(self, request):
        """
        Gets all articles
        """
        tags = Tag.objects.all()
        if not tags:
            response = Response(
                data={
                    "errors": {
                        "tags":
                        ["There are no tags in Authors Heaven at the moment"]
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            response = Response(
                data={
                    "tags": [tag.tag_name for tag in tags]
                },
                status=status.HTTP_200_OK
            )
        return response


class LikeDislikeView(GenericAPIView):
    """
    A generic class to like and dislike articles
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArticleSerializer

    def post(self, request, slug, vote_type):
        """
        A method to post a likes
        """
        article_inst = RetrieveUpdateArticleAPIView()
        article = article_inst.retrieve_article(slug)

        def get_vot_response(votetype):
            if vote_type == "dislike":
                article.votes.down(request.user.id)
                return_string = "Dislike posted successfully"
            else:
                article.votes.up(request.user.id)
                return_string = "Like posted successfully"
            return return_string
        serializer = ArticleSerializer(
            article,
            context={'article': slug, 'request': request, },
            many=False)
        vote_resp = get_vot_response(vote_type)
        response = Response({
            "article": serializer.data,
            "message": vote_resp
        }, status=status.HTTP_200_OK)

        return response

    def if_vote_exist(self, request, slug, vote):
        article = RetrieveUpdateArticleAPIView().retrieve_article(slug)
        if article.votes.exists(request.user.id, vote):
            return True
        return False

    def process_vote_type(self, request, slug, vote_type):
        vote_message = None
        voted = False
        if vote_type == "like" and self.if_vote_exist(request, slug, 0):
            vote_message = ["Like delete successfully"]
            voted = True
        elif vote_type == "dislike" and self.if_vote_exist(request, slug, 1):
            vote_message = ["Dislike delete successfully"]
            voted = True
        return vote_message, voted

    def delete(self, request, slug, vote_type):
        """
        A method to delete a vote for a certain article
        """

        # def get_vot_response(votetype):

        response, voted = self.process_vote_type(request, slug, vote_type)
        if voted:
            article = RetrieveUpdateArticleAPIView().retrieve_article(slug)
            serializer = ArticleSerializer(
                article,
                context={'article': slug, 'request': request, },
                many=False)
            return Response({
                "article": serializer.data,
                "message": response
            }, status=status.HTTP_200_OK)
        return Response({
            'errors': {
                'error': 'You have not {}d this article'.format(vote_type)
            }
        }, status=status.HTTP_404_NOT_FOUND)


class FavoritesView(GenericAPIView):
    """
    A class for posting favourite articles
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoritesSerializer

    def post(self, request, slug):
        """
        A method to favorite an article
        """
        data = request.data
        article_inst = RetrieveUpdateArticleAPIView()
        article = article_inst.retrieve_article(slug)
        favorite_count = article.favoritesCount
        user = request.user
        favorite = Favorite.objects.filter(user=user, article=article)
        if favorite:
            response = Response({
                'errors': {
                    'exist': ['Already favorited this article']
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            Article.objects.filter(slug=slug).update(
                favoritesCount=favorite_count + 1)
            data['article'] = article.id
            data['user'] = request.user.id
            serializer = FavoritesSerializer(data=data)
            serializer.is_valid()
            serializer.save()
            article_id = serializer.data.get("article")
            article = Article.objects.get(id=article_id)
            article_serializer = ArticleSerializer(
                article,
                context={'article': slug, 'request': request},
                many=False
            )
            response = Response({
                "article": article_serializer.data,
                "message": "Article added to favorites"
            }, status=status.HTTP_201_CREATED)

        return response

    def delete(self, request, slug):
        """
        A method to unfavorite an article
        """
        article_inst = RetrieveUpdateArticleAPIView()
        article = article_inst.retrieve_article(slug)

        favorite_count = article.favoritesCount
        favorite = Favorite.objects.filter(
            user=request.user.id, article=article)
        if favorite:
            favorite.delete()
            Article.objects.filter(slug=slug).update(
                favoritesCount=favorite_count-1)
            return Response({
                "message": "Article removed from favorites"
            }, status=status.HTTP_200_OK)
        return Response({
            'errors': {
                'exist': ['You have not favorited this article']
            }
        }, status=status.HTTP_404_NOT_FOUND)


class ListUserFavoriteArticlesView(GenericAPIView):
    """
    List all favorite articles by the user
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArticleSerializer

    def get(self, request):
        favorites = Favorite.objects.filter(
            user_id=request.user.id)
        user_favorites = []
        for favorite in favorites:
            article = Article.objects.get(id=favorite.article_id)
            article = ArticleSerializer(
                article,
                context={'article': article.slug, 'request': request},).data
            user_favorites.append(article)

        return Response(
            data={"favorites": user_favorites},
            status=status.HTTP_200_OK
        )


class RateArticleAPIView(GenericAPIView):
    """
    Rating an article from 1 - 5
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)

    query_set = RatingModel.objects.all()
    serializer_class = RatingSerializer

    def post(self, request, slug):
        """
        Method to post a rating on an article
        """
        rating_value = request.data
        article_instance = RetrieveUpdateArticleAPIView()
        article = article_instance.retrieve_article(slug)

        if article.author == request.user:
            raise ValidationError(
                detail={
                    "error": "You can't rate your own article"
                }
            )

        try:
            already_rated = RatingModel.objects.get(
                rated_by=request.user, article=article)
            serializer = self.serializer_class(
                already_rated, data=rating_value)
        except RatingModel.DoesNotExist:
            serializer = self.serializer_class(data=rating_value)

        serializer.is_valid(raise_exception=True)
        serializer.save(article=article, rated_by=request.user)
        serializer_article = ArticleSerializer(
            article,
            context={
                'article': article.slug, 'request': request}
        )
        article_data = serializer_article.data

        return Response(article_data, status=status.HTTP_201_CREATED)


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
        comment = request.data
        try:
            slug = self.kwargs['slug']
            article = Article.objects.get(slug=slug)
            request.POST._mutable = True
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
        self.serializer_class = DisplayCommentsSerializer

        article = Article.objects.filter(slug=slug)
        serializer = self.serializer_class(article, many=True)
        data = {}
        response = None
        response = get_serialiser_data(serializer, "comments")
        return response


class CommentDetailAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = CommentDetailSerializer

    def get(self, request, slug, id):
        """
        get a comment
        """
        self.serializer_class = DisplaySingleComment
        comment = Comment.objects.all().filter(id=id, article__slug=slug)
        serializer = self.serializer_class(comment, many=True)
        data = None
        response = None
        response = get_serialiser_data(serializer, "representation")
        return response

    def post(self, request, slug, id):
        """
        create a child comment
        """
        comment = request.data
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
        comment = request.data
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


class SocialShareArticleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, provider):
        """
        Generate sharing links for various social platforms
        """
        shared_article = RetrieveUpdateArticleAPIView().retrieve_article(slug)
        context = {'request': request}

        uri = request.build_absolute_uri()

        article_uri = uri.rsplit('share/', 1)[0]
        try:
            share_link = generate_share_url(
                context, provider, shared_article, article_uri)

            if share_link:
                return Response({
                    "share": {
                        "provider": provider,
                        "link": share_link
                    }
                })
        except KeyError:
            return Response({
                "message": "Please select a valid provider - twitter, "
                           "facebook, email, telegram, linkedin, reddit"
            }, status=200)
