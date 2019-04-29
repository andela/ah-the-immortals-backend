from django.core.exceptions import ValidationError

from rest_framework.generics import GenericAPIView
from rest_framework import permissions, status
from rest_framework.response import Response

from .serializers import UserProfileSerializer, UpdateUserProfileSerializer

from .models import Profile


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
                 "error": "User does not exist"
             }, status = status.HTTP_404_NOT_FOUND)

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
                 "error": "User does not exist"
             }, status = status.HTTP_404_NOT_FOUND)
        user_name = request.user.username
        if user_name != username:
            return Response({
                'error': 'You do not own this profile'
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
