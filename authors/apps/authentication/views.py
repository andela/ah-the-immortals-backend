from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from social_django.utils import load_backend, load_strategy
from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.exceptions import MissingBackend

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    SocialAuthSerializer
)


class RegistrationAPIView(GenericAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class SocialAuthAPIView(CreateAPIView):
    """
    Social authentication using Google, Facebook and Twitter
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = SocialAuthSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        authenticated_user = request.user if not request.user.is_anonymous else None
        # The social provider given in the request
        # Facebook, Twitter, Google
        provider = serializer.data.get('provider')
        # expects to use django
        strategy = load_strategy(request)
        try:
            # checks the backend of the social auth provider in the request
            backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)
        except MissingBackend:
            # exception thrown if backend for the given provider is not available
            return Response({"error": "Provider invalid or not supported"},
                            status=status.HTTP_404_NOT_FOUND)
        # token in the OAuth2 request for facebook and google
        # requires only the access token
        # OAuth1 is used by twitter and requires the token and the token secret
        if isinstance(backend, BaseOAuth1):
            token = {
                'oauth_token': serializer.data.get('access_token'),
                'oauth_token_secret': serializer.data.get('access_token_secret')
                }
        elif isinstance(backend, BaseOAuth2):
            token = serializer.data.get('access_token')
        try:
            # if a user with the credentials does not exist, a new user is created
            # Otherwise if they exist they are just logged in to their account
            user = backend.do_auth(token, user=authenticated_user)
        except BaseException as e:
            # Throws an error if the request tries to associate one social account with multiple users 
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        # persist to database if new user and return the user object
        if user and user.is_active:
            user.is_verified = True
            user.save()
            serializer = UserSerializer(user)
            serializer.instance = user
            return Response(serializer.data, status=status.HTTP_200_OK)
