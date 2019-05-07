import jwt
from datetime import datetime, timedelta
from django.conf import settings
import json
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
from django.utils import timezone

User = get_user_model()


class BaseTest(APITestCase):
    """
    The base test case for all authentication test cases
    """
    client = APIClient()

    def setUp(self):
        """
        test method for all settings
        """
        self.login_url = reverse("authentication:login")
        self.register_url = reverse("authentication:registration")
        self.update_url = reverse("authentication:update_get")
        self.get_url = reverse("authentication:update_get")
        # self.verification_of_user = reverse("authentication:signup_verification")
        self.user = User.objects.create_user(
            username="adam",
            email="adam@gmail.com",
            password="@Us3r.co3mW",
        )
        self.user.is_verified = True
        self.user.save()

        self.user1 = User.objects.create_user(
            username="ian",
            email="ian@gmail.com",
            password="@Us3r.co3mW",
        )
        self.user1.is_verified = True
        self.user1 = User.objects.get(username='ian')
        self.user1.is_active = False
        self.user1.save()

        self.user2 = User.objects.create_user(
            username="theonly",
            email="ianissa@gmail.com",
            password="@Us3r.co3mW",
        )

        self.user3 = User.objects.create_user(
            username="Escobar",
            email="pablo@escobar.com",
            password="@Us3r.co3mW",
        )

        self.user4 = User.objects.create_user(
            username="Elchapo",
            email="el@chapo.com",
            password="@Us3r.co3mW",
        )

        self.user4.is_verified = True
        self.user4.save()

        self.super_user = User.objects.create_superuser(
            username="admin",
            email="admin@authors.com",
            password="adm123Pass!!",
        )

    def generate_jwt_token(self, email, username):
        """
        Generates a JSON Web Token to be used in testing
        """
        user_details = {'email': email,
                        'username': username}
        token = jwt.encode(
            {
                'user_data': user_details,
                'exp': datetime.now() + timedelta(hours=24)
            }, settings.SECRET_KEY, algorithm='HS256'
        )
        return token.decode('utf-8')

    def generate_expired_token(self):
        """
        Generates a token that expires after one second for testing purposes
        """
        user_details = {'email': "ianissa@gmail.com",
                        'username': "theonly"}
        token = jwt.encode(
            {
                'user_data': user_details,
                'exp':  datetime(2018, 7, 12)
            }, settings.SECRET_KEY, algorithm='HS256'
        )
        return token.decode('utf-8')

    def signup_user(self, username="", email="", password=""):
        """
        Method to register a user
        """
        return self.client.post(
            self.register_url,
            data=json.dumps({
                "user": {
                    "username": username,
                    "email": email,
                    "password": password
                }
            }),
            content_type="application/json"
        )

    def signup_user_with_missing_key(self, email="", password=""):
        """
        Method to register a user
        """
        return self.client.post(
            self.register_url,
            data=json.dumps({
                "user": {
                    "email": email,
                    "password": password
                }
            }),
            content_type="application/json"
        )

    def login_user(self, email="", password=""):
        """
        A method to login a user
        """
        return self.client.post(
            self.login_url,
            data=json.dumps({
                "user": {
                    "email": email,
                    "password": password
                }
            }),
            content_type="application/json"
        )

    def is_authenticated(self, email="", password=""):
        return self.client.login(username=email, password=password)

    def update_user(self, username="", email="", password=""):
        """
        A method to update user
        """
        return self.client.put(
            self.update_url,
            data=json.dumps({
                "user": {
                    "username": username,
                    "email": email,
                    "password": password
                }
            }),
            content_type="application/json"
        )

    def get_user(self):
        """
        A method to retrieve users from the database
        """
        return self.client.get(self.get_url)

    def authenticate_user(self, email, password):
        """
        Authenticates users by adding authorization headers
        """
        logdata = self.login_user(email, password)
        token = logdata.data['token']
        return self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)

    def social_login(self, social_url, social_user):
        """
        Method to login user using social authentication
        """
        return self.client.post(social_url, social_user)

    def verify_user(self, email=""):
        """
        To verify a user
        """
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()


class PasswordResetBaseTest(BaseTest):
    """
    Base test for testing passeord reset
    """

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.email = self.user.email
        self.password_reset_url = reverse("authentication:password_reset")
        self.token = None
        self.password_reset_confirm_url = reverse(
            "authentication:password_reset_confirm")
        self.reset_data = {
            "user": {
                "email": self.email
            }
        }
        self.password_data = {
            "password": "HenkDTestPAss23!#",
            "password_confirm": "HenkDTestPAss23!#"
        }
        self.contains_error = lambda container, error: error in container

    def password_reset(self):
        """
        Verifies user account and generates reset password
        token
        """
        response = self.client.post(
            path=self.password_reset_url,
            data=self.reset_data,
            format="json"
        )
        token, created = Token.objects.get_or_create(user=self.user)
        self.token = token.key
        self.set_password_confirm_url()
        return response

    def generate_fake_token(self):
        """
        Generates invalid token
        """
        self.token = "fjeojfoeefubbfbwuebbyvyfvwd24"
        self.set_password_confirm_url()

    def generate_expired_token(self):
        """
        Generates expired token
        """
        token, created = Token.objects.get_or_create(user=self.user)
        token.created = timezone.now()-timezone.timedelta(hours=25)
        token.save()
        self.token = token.key
        self.set_password_confirm_url()

    def set_password_confirm_url(self):
        """
        Sets password confirm url as the token changes
        """
        self.password_reset_confirm_url += '?token='+self.token

    def password_reset_confirm(self):
        """
        Confirms password reset by posting new password
        """
        response = self.client.post(
            path=self.password_reset_confirm_url,
            data=self.password_data,
            format="json"
        )
        return response
