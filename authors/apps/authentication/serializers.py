from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password
from authors.utils.password_validators import get_password_policy_errors
from authors.utils.authentication_handlers import AuthTokenHandler


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='user with this email already exists'
            )
        ]
    )
    # Ensure passwords are at least 8 characters long, no longer than 30
    # Password has no spaces
    password = serializers.CharField(
        max_length=250,
        write_only=True,
        allow_null=True,
        allow_blank=True,
        required=True
    )

    def validate_password(self, value):
        errors = get_password_policy_errors(value)
        if errors:
            raise serializers.ValidationError(errors)
        return value

    # Username should be unique
    # Username should not have spaces or special characters
    # Underscores and hyphens are allowed
    username = serializers.RegexField(
        regex='^(?!.*\ )[A-Za-z\d\-\_]+$',
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='user with this username already exists',
            )
        ],
        error_messages={
            'invalid': 'Username can only contain letters, numbers, underscores, and hyphens',
            'required': 'Username is a required field'
        }
    )
    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username', 'password', 'token']

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(
        max_length=255, allow_blank=True)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(
        max_length=128, write_only=True, allow_blank=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if not email and not password:
            resp = {
                'email': 'An email address is required to log in.',
                'password': 'A password is required to log in.'
            }
            raise serializers.ValidationError(resp)

        if not email:
            resp = {
                'email': 'An email address is required to log in.'
            }
            raise serializers.ValidationError(resp)
        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if not password:
            resp = {
                'password': 'A password is required to log in.'
            }
            raise serializers.ValidationError(resp)

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` data. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            resp = {
                'credentials': 'Wrong email or password.'
            }
            raise serializers.ValidationError(resp)

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token,
        }


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These datas are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'token', 'password')

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and
        # `max_length` properties too, but that isn't the case for the token
        # field.

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # This is because Django provides a function that handles hashing and
        # salting passwords, which is important for security. What that means
        # here is that we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()` is the method mentioned above. It handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # Finally, after everything has been updated, we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance


class SocialAuthSerializer(serializers.Serializer):

    provider = serializers.CharField(
        max_length=30,
        allow_blank=True
    )
    access_token = serializers.CharField(
        max_length=255,
        allow_blank=True
    )
    access_token_secret = serializers.CharField(
        max_length=255,
        allow_blank=True,
        default=""
    )

    def validate(self, data):
        """Method to validate provider and access token"""
        provider = data.get('provider', None)
        access_token = data.get('access_token', None)
        access_token_secret = data.get('access_token_secret', None)
        if not provider:
            raise serializers.ValidationError(
                'A provider is required for Social Login'
            )

        if not access_token:
            raise serializers.ValidationError(
                'An access token is required for Social Login'
            )

        if provider == 'twitter' and not access_token_secret:
            raise serializers.ValidationError(
                'An access token secret is required for Twitter Login'
            )
        return data


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset
    """
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True
    )

    def validate(self, data):
        email = data.get("email")
        if not email:
            raise serializers.ValidationError({
                "email": "Please provide your email address"
            })
        if not EmailValidator(email):
            raise serializers.ValidationError({
                "email": "Enter a valid email address."
            })
        try:
            User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                "email": "No account with that email address"
            })
        return data


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer class for password reset confirm
    """
    token = serializers.CharField(
        max_length=250,
        write_only=True,
        allow_null=True,
        allow_blank=True,
        required=False
    )
    password = serializers.CharField(
        max_length=250,
        write_only=True,
        allow_null=True,
        allow_blank=True,
        required=False
    )
    password_confirm = serializers.CharField(
        max_length=250,
        write_only=True,
        allow_null=True,
        allow_blank=True,
        required=False
    )

    def validate(self, data):
        if not data.get("token"):
            raise serializers.ValidationError({
                "token": "There is no token provided"
            })
        try:
            token_object = Token.objects.get(key=data.get("token"))
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                "token": "Invalid token"
            })
        if AuthTokenHandler.expired_token(token_object):
            raise serializers.ValidationError({
                "token": "Expired token"
            })
        self.get_password_field_erros(data)
        try:
            validate_password(data.get("password"))
        except ValidationError as error:
            raise serializers.ValidationError({
                "password": list(error)
            })
        password_errors = get_password_policy_errors(data.get("password"))
        if password_errors:
            raise serializers.ValidationError({
                "password": list(password_errors)
            })
        return data

    def get_password_field_erros(self, data):
        """
        Captures null, blank and empty fields for password
        and password confirm
        """
        if not data.get("password") and not data.get("password_confirm"):
            raise serializers.ValidationError({
                "password": "Please provide your password",
                "password_confirm": "Please confirm your password"
            })
        elif not data.get("password"):
            raise serializers.ValidationError({
                "password": "Please provide your password"
            })
        elif not data.get("password_confirm"):
            raise serializers.ValidationError({
                "password_confirm": "Please confirm your password"
            })
        elif data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({
                "password": "Passwords did not match"
            })
