from django.core.exceptions import ValidationError

from rest_framework.generics import GenericAPIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from authors.apps.authentication.models import User
from django.shortcuts import get_object_or_404

from .serializers import UserProfileSerializer, UpdateUserProfileSerializer, FollowingSerializer, UserListSerializer
from .models import Profile, Followers
from .renderers import FollowersJSONRenderer


class UserProfileView(GenericAPIView):
    """
    A class for getting user profile
    """
    permission_classes = [permissions.IsAuthenticated]
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

        serializer = UserProfileSerializer(
            profile, context={'request': request}
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

    permission_classes = (IsAuthenticated,)
    renderer_classes = (FollowersJSONRenderer,)
    serializer_class = FollowingSerializer

    def is_following_user(self, profile, followed):
        if profile.id == followed.id:
            return Response({
                'error': 'You can not follow yourself.'
            }, status=status.HTTP_400_BAD_REQUEST)
        qs = Followers.objects.filter(
            profile_id=profile.id, followed_id=followed.profile.id).first()
        if qs:
            return Response({
                "error": "You are already following {}.".format(followed.username)
            }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, username):

        profile = User.objects.get(username=request.user.username)
        followed = get_object_or_404(User, username=username)

        verify_follow = self.is_following_user(profile, followed)
        if isinstance(verify_follow, Response):
            return verify_follow
        serializer_data = {
            'profile': profile.id,
            'followed': followed.profile.id}
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        profile = Profile.objects.get(user_id=profile.pk)
        response = {
            "username": followed.username,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "bio": profile.bio,


        }
        return Response(response, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, username):
        profile = User.objects.get(username=request.user.username)
        followed = get_object_or_404(User, username=username)
        follow = Followers.objects.filter(
            profile_id=profile.id, followed_id=followed.profile.id).first()
        if not follow:
            return Response({
                'error': 'you have to be following the user in order to unfollow.'
            }, status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        profile = Profile.objects.get(user_id=followed.pk)
        response = {
            "username": followed.username,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "bio": profile.bio,

        }
        return Response(response, status=status.HTTP_202_ACCEPTED)

    def get(self, request, username):
        """get all users a user is following"""
        user = get_object_or_404(User, username=username)
        follows = Followers.objects.filter(profile_id=user.id)
        serializer = self.serializer_class(follows, many=True)
        profiles = []
        for follow in serializer.data:
            profile = Profile.objects.get(id=follow['followed'])
            profiles.append({
                "username": profile.user.username,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "bio": profile.bio,
            })
        if not profiles:
            response = {'message': '{} has no followings yet'.format(username)}
        else:
            response = {
                'count': len(profiles), 'current_followings': profiles}
        return Response(response, status=status.HTTP_200_OK)


class FollowersAPI(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (FollowersJSONRenderer,)
    serializer_class = FollowingSerializer

    def get(self, request, username):
        """ Get all Users following a user """

        user = get_object_or_404(User, username=username)
        followers = Followers.objects.filter(profile_id=user.id)
        serializer = self.serializer_class(followers, many=True)
        profiles = []
        for follow in serializer.data:
            profile = Profile.objects.get(id=follow['followed'])
            user = User.objects.get(id=follow['profile'])
            profiles.append({
                "username": profile.user.username,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "bio": profile.bio,
            })
        if not profiles:
            response = {
                'message': '{} has no followers yet'.format(username)}
        else:
            response = {
                'count': len(profiles), 'current_followers': profiles}
        return Response(response, status=status.HTTP_200_OK)


class UserListView(GenericAPIView):
    """
    A class for getting all user profiles
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Profile.objects.all()
        serializer = UserListSerializer(queryset, many=True)
        return Response({
            'profiles': serializer.data
        }, status=status.HTTP_200_OK)
