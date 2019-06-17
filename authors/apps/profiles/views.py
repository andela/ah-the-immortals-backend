from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from authors.apps.authentication.models import User
from .exceptions import *
import json
from .serializers import (
    UserProfileSerializer, UpdateUserProfileSerializer,
    FollowingSerializer, FollowersListSerializer, UserListSerializer)

from authors.apps.articles.serializers import ArticleSerializer
from authors.apps.articles.models import Article
from .models import Profile
from .renderers import FollowersJSONRenderer


class UserProfileView(GenericAPIView):
    """
    A class for getting user profile
    """
    permission_classes = (AllowAny,)
    serializer_class = UserProfileSerializer

    def get(self, request, username):
        """
        Endpoint for fetching user data from Profile model
        """
        try:
            profile = Profile.objects.get(user__username=username)
        except Exception:
            return Response({
                'errors': {
                    'user': ['User does not exist']
                }
            }, status=status.HTTP_404_NOT_FOUND)
        articles = Article.objects.filter(author__username=username)
        articles_serializer = ArticleSerializer(
            articles, many=True, context={'request': request},
            remove_fields=['like_info', 'comments', 'favorites', 'ratings']
        )
        articles = articles_serializer.data
        if request.user.username == username:
            serializer = UserProfileSerializer(
                profile, context={'request': request, 'articles': articles},
                remove_fields=['following']
            )
        else:
            serializer = UserProfileSerializer(
                profile, context={'request': request, 'articles': articles}
            )
        return Response({
            'profile': serializer.data
        }, status=status.HTTP_200_OK)


class UpdateUserProfileView(GenericAPIView):
    """
    A class for updating user profile
    """
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UpdateUserProfileSerializer

    def patch(self, request, username):
        """
        Endpoint for updating user profile with the neccessary data
        """
        try:
            profile = Profile.objects.get(user__username=username)
        except Exception:
            return Response({
                'errors': {
                    'user': ['User does not exist']
                }
            }, status=status.HTTP_404_NOT_FOUND)
        user_name = request.user.username
        if user_name != username:
            return Response({
                'errors': {
                    'user': ['You do not own this profile']
                }
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        serializer = UpdateUserProfileSerializer(
            instance=request.user.profile,
            data=data,
            partial=True
        )
        serializer.is_valid()
        serializer.save()
        return Response(
            {'profile': serializer.data},
            status=status.HTTP_200_OK
        )


class FollowAPI(GenericAPIView):
    """class for follow and unfollow users"""
    permission_classes = (IsAuthenticated,)
    renderer_classes = (FollowersJSONRenderer,)
    serializer_class = FollowingSerializer

    def post(self, request, username):
        """Follow a certain user"""

        try:
            the_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise UserNotFound

        if the_user.id == request.user.id:
            APIException.status_code = status.HTTP_400_BAD_REQUEST
            raise APIException({"message": "You cannot follow yourself"})

        to_follow = Profile.objects.get(user_id=the_user.id)
        my_profile = request.user.profile
        if my_profile.if_following(to_follow):
            APIException.status_code = status.HTTP_400_BAD_REQUEST
            raise APIException(
                {"message": "You already follow {}".format(the_user.username)})

        my_profile.follow(to_follow)
        return Response({"message": "You now follow {}"
                         .format(the_user.username)})

    def delete(self, request, username):
        """Unfollow a certain user"""
        try:
            the_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise UserNotFound
        to_follow = Profile.objects.get(user_id=the_user.id)
        my_profile = request.user.profile
        if not my_profile.if_following(to_follow):
            APIException.status_code = status.HTTP_400_BAD_REQUEST
            raise APIException(
                {"message": "You do not follow {}"
                    .format(the_user.username)})
        my_profile.unfollow(to_follow)
        return Response({"message": "You have unfollowed {}"
                         .format(the_user.username)})

    def get(self, request, username):
        """get all users a user is following"""
        try:
            the_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise UserNotFound
        to_check = Profile.objects.get(user_id=the_user.id)
        my_follows = to_check.following_list()
        serializer = UserProfileSerializer(my_follows, many=True)
        return Response({"following": serializer.data,
                         "count": len(serializer.data)},
                        status=status.HTTP_200_OK)


class MyFollowersAPI(GenericAPIView):
    """class for followers"""
    permission_classes = (IsAuthenticated,)
    renderer_classes = (FollowersJSONRenderer,)
    serializer_class = UserProfileSerializer

    def get(self, request, username):
        """get all my followers"""
        try:
            the_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise UserNotFound
        to_check = Profile.objects.get(user_id=the_user.id)
        my_follows = to_check.w_following.all()
        serializer = self.get_serializer(my_follows, many=True)
        return Response({"followers": serializer.data, "count":
                         len(serializer.data)},
                        status=status.HTTP_200_OK)


class UserListView(ListAPIView):
    """
    A class for getting all user profiles
    """
    permission_classes = (AllowAny,)
    serializer_class = UserProfileSerializer
    queryset = Profile.objects.all()

    def list(self, request):
        queryset = self.queryset.filter()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'profiles': serializer.data
        }, status=status.HTTP_200_OK)
