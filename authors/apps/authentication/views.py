from .backends import JWTAuthentication
from ..utils.mailer import ConfirmationMail
import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, exceptions

from social_django.utils import load_backend, load_strategy
from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.exceptions import MissingBackend

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    SocialAuthSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer
)
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.authentication import (
    TokenAuthentication,
    get_authorization_header
)
from authors.utils.mailer import VerificationMail
from django.utils import timezone

User = get_user_model()


class RegistrationAPIView(GenericAPIView):
    """
    signup a user
    """
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        ConfirmationMail(serializer.data).send_mail()
        message = {
            "user": {
                "email": serializer.data.get('email'),
                "username": serializer.data.get("username"),
                "token": serializer.data.get("token")
            },
            "message":
            "Account created successfully. Check your email."
        }
        return Response(message, status=status.HTTP_201_CREATED)


class LoginAPIView(GenericAPIView):
    """
    login a user
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    Retrieve and update users
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Get the currently login user
        """
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        update users
        """
        serializer_data = request.data

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
        provider = serializer.data.get('provider')
        strategy = load_strategy(request)
        try:
            backend = load_backend(
                strategy=strategy, name=provider, redirect_uri=None)
        except MissingBackend:
            return Response({"error": "Provider invalid or not supported"},
                            status=status.HTTP_404_NOT_FOUND)
        if isinstance(backend, BaseOAuth1):
            token = {
                'oauth_token': serializer.data.get('access_token'),
                'oauth_token_secret': serializer.data.get('access_token_secret')
            }
        elif isinstance(backend, BaseOAuth2):
            token = serializer.data.get('access_token')
        try:
            user = backend.do_auth(token, user=authenticated_user)
        except BaseException as e:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        if user and user.is_active:
            user.is_verified = True
            user.save()
            serializer = UserSerializer(user)
            serializer.instance = user
            return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetView(GenericAPIView):
    """
    Sends password reset email with id token
    """
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        email = data.get("email")
        user = User.objects.get(email=email)
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            token.created = timezone.now()
            token.save()
        VerificationMail(user, token).send_mail()
        response = Response(
            data={"data": [{
                "message": "A password reset link has been sent to your email"
            }]},
            status=status.HTTP_200_OK
        )
        return response


class PasswordResetConfirmView(GenericAPIView):
    """
    Confirms password reset after retrieving token embedded in mail
    """
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        request.POST._mutable = True
        data = request.data
        token, password = (
            request.GET.get("token"),
            data.get("password")
        )
        data["token"] = token
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        token_object = Token.objects.get(key=token)
        user = token_object.user
        user.set_password(password)
        user.save()
        token_object.delete()
        response = Response(
            data={"data": [{
                "message": "You have successfully reset your password"
            }]},
            status=status.HTTP_200_OK
        )
        return response


class SignupEmailVerificationView(GenericAPIView):
    """ Verification of email """

    def get(self, request, token):
        try:
            user_information = jwt.api_jwt.decode(
                token, settings.SECRET_KEY, algorithms='HS256')
        except jwt.api_jwt.DecodeError:
            raise exceptions.AuthenticationFailed(
                'Invalid Token. The token provided cannot be decoded!'
            )
        except jwt.api_jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                'The token used has expired. Please authenticate again!'
            )

        user_email = user_information['user_data']['email']
        user = User.objects.get(email=user_email)
        if user.is_verified:
            return Response({
                "message": "Your email is already verified"
            }, status.HTTP_406_NOT_ACCEPTABLE)
        user.is_verified = True
        user.save()
        return Response({
            "message": "You have been verified successfully"
        }, status.HTTP_200_OK)
