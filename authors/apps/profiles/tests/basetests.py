import json
import base64

from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token

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
        self.user = User.objects.create_user(
            username="adam",
            email="adam@gmail.com",
            password="@Us3r.com"
        )

        self.user.is_verified = True
        self.user.save()

        self.user1 = User.objects.create_user(
            username="eri",
            email="eric@gmail.com",
            password="@Us3r.com"
        )

        self.user1.is_verified = True
        self.user1.save()

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
        """Authenticate user before posting data
        """
        logdata = self.login_user(email, password)
        token = logdata.data['token']
        return self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)

    def get_profile_with_valid_username(self):
        """
        Method to get profile while the provided credentials are correct
        """
        username = str(self.user.username)
        url = reverse("profiles:profile", args=[username])
        response = self.client.get(url)
        return response

    def get_profile_with_invalid_username(self):
        """
        Method to get profile while the provided credentials are incorrect
        """
        url = reverse("profiles:profile", args=["username"])
        response = self.client.get(url)
        return response

    def update_user_profile(self, first_name="", last_name="", bio=""):
        """
        Method to update user profile successfully
        """
        username = str(self.user.username)
        url = reverse("profiles:update_profile", args=[username])
        return self.client.patch(
            url,
            data=json.dumps(
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "bio": bio
                }
            ),
            content_type="application/json"
        )

    def update_another_user_profile(self, first_name="", last_name="", bio=""):
        """
        Method to update user profile successfully
        """
        username = str(self.user1.username)
        url = reverse("profiles:update_profile", args=[username])
        return self.client.patch(
            url,
            data=json.dumps(
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "bio": bio
                }
            ),
            content_type="application/json"
        )

    def update_user_profile_notexist(self, first_name="", last_name="", bio=""):
        """
        Method to update user profile successfully
        """
        url = reverse("profiles:update_profile", args=["username"])
        return self.client.patch(
            url,
            data=json.dumps(
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "bio": bio
                }
            ),
            content_type="application/json"
        )

    def list_profiles(self):
        """
        Method to get all profiles
        """
        urls = reverse("profiles:list_users")
        response = self.client.get(urls)
        return response
