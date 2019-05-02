import jwt
from datetime import datetime, timedelta
from django.conf import settings
import json
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse

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
        self.user = User.objects.create_user(
            username="adam",
            email="adam@gmail.com",
            password="@Us3r.com"
        )

        self.user1 = User.objects.create_user(
            username="ian",
            email="ian@gmail.com",
            password="Maina9176",
        )
        self.user1 = User.objects.get(username='ian')
        self.user1.is_active = False
        self.user1.save()

        self.user2 = User.objects.create_user(
            username="theonly",
            email="ianissa@gmail.com",
            password="Maina9176",
        )

        self.super_user = User.objects.create_superuser(
            username="admin",
            email="admin@authors.com",
            password="adm123Pass!!"
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
