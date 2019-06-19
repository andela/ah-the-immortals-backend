import types

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
from .exceptions import (ArticleNotFound, BookmarkDoesNotExist, Forbidden,
                         ItemDoesNotExist)
from .filters import ArticleFilter
from .models import (Article, Bookmarks, Comment, CommentHistory, Favorite,
                     LikeDislikeComment, RatingModel, Tag)
from .serializers import (
    ArticlePaginator, ArticleSerializer,
    BookmarkSerializers, CommentChildSerializer,
    CommentDetailSerializer,
    CommentEditHistorySerializer, CommentSerializer,
    DisplayCommentsSerializer, DisplaySingleComment,
    FavoritesSerializer, RatingSerializer, add_tag_list
)


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
                           'favorites', 'ratings'],
            context={"request": request}
        )
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
        serializer = ArticleSerializer(
            result, many=True,
            context={'request': request},
            remove_fields=[
                'like_info',
                'comments',
                'favorites',
                'ratings'
            ]
        )
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
                               'favorites', 'ratings'],
                context={"request": request}
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
            article.votes.delete(request.user.id)
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
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
        serializer = self.serializer_class(
            article,
            many=True,
            context={"request": request}
        )
        data = {}
        response = None
        response = get_serialiser_data(serializer, "comments",)
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
        serializer = self.get_serializer(
            comment,
            many=True,
            context={"request": request}
        )
        data = None
        response = None
        response = get_serialiser_data(serializer, "representation")
        return response
        # return Response({"comment": serializer.data})

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
            comment_body = comment_obj.body
            input_comment = comment.get("body").strip()
            db_comment = comment_body.strip()
            if comment_obj.author == request.user and \
                    input_comment == db_comment:
                serializer = self.serializer_class(
                    comment_obj, context={'comment': Id},)
                comment_string = "No changes detected on the comment"
                return Response({
                    "comment": serializer.data,
                    "message": comment_string
                })
            elif comment_obj.author == request.user:
                history_serializer = CommentEditHistorySerializer(
                    data={"body": comment_body},
                    remove_fields=['id', 'created_at']
                )
                history_serializer.is_valid(raise_exception=True)
                history_serializer.save(commentId=comment_obj)
                comment['author'] = request.user.id
                comment['article'] = article.id
                serializer = self.serializer_class(
                    comment_obj, data=comment, context={'comment': Id},
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                comment_string = "Comment updated successfuly"
                return Response({
                    "comment": serializer.data,
                    "message": comment_string
                })
            else:
                raise Forbidden
        except Comment.DoesNotExist:
            return Response(
                {
                    "error": {
                        "body": ["unsuccesful update either the comment or"
                                 "slug not found"
                                 ]}},
                status=status.HTTP_404_NOT_FOUND
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


class CommentOneHistoryView(GenericAPIView):
    """
    A view class for handling all operations made to
    Comment history models directly
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CommentEditHistorySerializer

    def get(self, request, slug, comment, id):
        """
        A view method to get one history comment for a comment
        """
        comment_history = CommentHistory.objects.all().filter(
            id=id, commentId=comment).first()
        serializer = self.serializer_class(comment_history, many=False)
        if serializer.data.get("body") == "":
            response = Response({
                "error": "History comment selected does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        else:
            response = Response({
                "comment_history": serializer.data
            }, status=status.HTTP_200_OK)
        return response


class CommentAllHistoryView(GenericAPIView):
    """
    A view class for handling all operations made to
    Comment history models directly
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CommentEditHistorySerializer

    def get(self, request, slug, comment):
        """
        A view method to get one history comment for a comment
        """
        comment_history = CommentHistory.objects.all().filter(
            commentId=comment
        )
        comment_hist = []
        if comment_history:
            for history in comment_history:
                serializer = self.serializer_class(history, many=False)
                comment_data = serializer.data
                comment_hist.append(comment_data)
            response = Response({
                "comments_history": comment_hist
            }, status=status.HTTP_200_OK)
        else:
            response = Response({
                "message": "No history comments",
                "comment": comment_hist
            }, status=status.HTTP_200_OK)
        return response


class BookmarkAPIView(GenericAPIView):
    """
    class for posting a bookmark
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BookmarkSerializers

    def post(self, request, **kwargs):
        """
        Bookmark an article
        """
        try:
            data = request.data
            user = request.user
            slug = self.kwargs['slug']
            article = Article.objects.get(slug=slug)
            bookmarks = Bookmarks.objects.filter(user=user, article=article)
            if bookmarks:
                response = Response({
                    'errors': {
                        'body': ['You already bookmarked this article']
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                data['article'] = article.id
                data['user'] = request.user.id
                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                article_id = serializer.data.get("article")
                article = Article.objects.get(id=article_id)
                serializer = ArticleSerializer(
                    article,
                    context={'article': slug, 'request': request},
                    many=False
                )
                response = Response({
                    "article": serializer.data,
                    "message": "Article Bookmarked succefully"
                }, status=status.HTTP_201_CREATED)

                return response
            return Response({"message": "Article has already been bookmarked"},
                            status.HTTP_400_BAD_REQUEST)
        except Article.DoesNotExist:
            raise ArticleNotFound


class GetBookMarksAPIVIew(GenericAPIView):
    """
    class for  getting bookmarks
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer

    def get(self, request):
        """
        Get all bookmarks for a user
        """
        user = request.user
        bookmarks = Bookmarks.objects.all().filter(user=user)
        if not bookmarks:
            return Response({"message": "Bookmarks not found"},
                            status.HTTP_404_NOT_FOUND)
        bookmarks = Bookmarks.objects.filter(user__pk=request.user.pk)
        data = []
        articles = [bookmark.article for bookmark in bookmarks]
        for article in articles:
            serializer = ArticleSerializer(
                article,
                remove_fields=[
                    'like_info',
                    'favorites',
                    'ratings'
                ],
                context={'request': request},
                many=False
            )
            data.append(serializer.data)
        response = Response({
            "articles": data,
        }, status=status.HTTP_200_OK)
        return response


class DeleteBookMakeAPIView(GenericAPIView):
    """
    class for deleting a bookmark
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BookmarkSerializers

    def delete(self, request, slug):
        """
        Remove a bookmark
        """
        try:

            inst = RetrieveUpdateArticleAPIView()
            article = inst.retrieve_article(slug)
            article = Article.objects.get(slug=slug)
            book = Bookmarks.objects.filter(
                user=request.user.id, article=article)
            if book:
                book.delete()
                return Response({"message": "Bookmark has been removed"},
                                status.HTTP_200_OK)
            return Response({"message": "Permission denied"},
                            status.HTTP_403_FORBIDDEN)
        except Bookmarks.DoesNotExist:
            raise BookmarkDoesNotExist


class LikeCommentsView(GenericAPIView):
    """ View class to handle liking of comments """
    permission_classes = (IsAuthenticated, )
    serializer_class = DisplaySingleComment

    def like_comment(self, comment, user):
        """
        Likes a comment
        """
        LikeDislikeComment.objects.create(
            user=user,
            comment=comment,
            like=True
        )

    def dislike_comment(self, comment, user):
        """
        Dislikes a comment
        """
        LikeDislikeComment.objects.create(
            user=user,
            comment=comment,
            dislike=True
        )

    def remove_like(self, comment, user):
        """
        Removes a like
        """
        LikeDislikeComment.objects.get(
            comment=comment,
            user=user,
            like=True
        ).delete()

    def remove_dislike(self, comment, user):
        """
        Removes a dislike
        """
        LikeDislikeComment.objects.get(
            comment=comment,
            user=user,
            dislike=True
        ).delete()

    def like(self, user, comment, message, request):
        """
        Handles comment like
        """
        if comment.liked(request):
            self.remove_like(comment, user)
            message = "Comment unliked"
        elif comment.disliked(request):
            self.remove_dislike(comment, user)
            self.like_comment(comment, user)
        else:
            self.like_comment(comment, user)
        return message

    def dislike(self, user, comment, message, request):
        """
        Handles comment dislike
        """
        if comment.disliked(request):
            self.remove_dislike(comment, user)
            message = "Dislike removed"
        elif comment.liked(request):
            self.remove_like(comment, user)
            self.dislike_comment(comment, user)
        else:
            self.dislike_comment(comment, user)
        return message

    def give_like(self, request, comment, vote_type):
        """
        Gives a like or dislike depending on like type
        """
        message = None
        user = request.user
        if vote_type == "like":
            message = "Comment liked"
            message = self.like(user, comment, message, request)
        elif vote_type == "dislike":
            message = "Comment disliked"
            message = self.dislike(user, comment, message, request)
        serializer = self.get_serializer(
            comment,
            many=False
        )
        data = serializer.data.get("representation")
        return data, message

    def post(self, request, id, vote_type):
        try:
            comment = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            APIException.status_code = status.HTTP_404_NOT_FOUND
            raise APIException({"message": "comment does not exist"})
        data, message = self.give_like(request, comment, vote_type)
        return Response({
            "comment": data,
            "message": message
        })
