from rest_framework import serializers

from .models import Profile
from .models import Followers


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer class for getting user profile
    """
    username = serializers.ReadOnlyField(source='fetch_username')
    img_url = serializers.ReadOnlyField(source='fetch_image')
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Profile
        fields = (
            'username', 'first_name', 'last_name', 'bio', 'img_url', 'created_at', 'updated_at'
        )


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer class for updating user profile
    """
    class Meta:
        model = Profile
        fields = (
            'first_name', 'last_name', 'bio', 'image'
        )


class FollowingSerializer(serializers.ModelSerializer):
    """"
    Serializer class to get the users following the user
    """

    class Meta:
        model = Followers
        fields = ('profile', 'followed')


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer class for getting user profile
    """
    username = serializers.ReadOnlyField(source='fetch_username')
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Profile
        exclude = ('user', 'id', )
