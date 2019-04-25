import json, base64

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

        self.super_user = User.objects.create_superuser(
            username="admin",
            email="admin@authors.com",
            password="adm123Pass!!"
        )

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
        self.client.login(username=email, password=password)

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
