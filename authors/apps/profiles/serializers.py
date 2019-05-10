from rest_framework import serializers

from .models import Profile
from authors.utils.baseserializer import BaseSerializer


class UserProfileSerializer(BaseSerializer):
    """
    Serializer class for getting user profile
    """

    def __init__(self, *args, **kwargs):
        super(UserProfileSerializer, self).__init__(*args, **kwargs)

    username = serializers.ReadOnlyField(source='fetch_username')
    img_url = serializers.ReadOnlyField(source='fetch_image')
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    following = serializers.SerializerMethodField()

    def get_following(self, instance):
        request = self.context.get('request', None)

        if request is None:
            return None
        if request.user.is_anonymous:
            return False

        my_profile = request.user.profile
        follow_status = my_profile.if_following(instance)
        return follow_status

    class Meta:
        model = Profile
        fields = (
            'username', 'first_name', 'last_name', 'bio', 'img_url', 'created_at', 'updated_at', 'following'
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
    username = serializers.CharField(
        source='user.username', read_only=True)
    Following = serializers.BooleanField(default=True)

    class Meta:
        model = Profile
        fields = ['username', 'first_name',
                  'last_name', 'bio', 'image', 'Following']


class FollowersListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'bio', 'image']


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer class for getting user profile
    """
    class Meta:
        model = Profile
        fields = '__all__'
