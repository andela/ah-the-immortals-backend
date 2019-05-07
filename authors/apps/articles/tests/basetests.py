from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
import json

User = get_user_model()


class BaseTest(APITestCase):
    """
    Class to set up test case
    """
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("authentication:login")
        self.create_url = reverse("articles:article")
        self.modify_url = reverse("articles:articles")

        self.user1 = User.objects.create_user(
            username="adam",
            email="adam@gmail.com",
            password="@Us3r.com"
        )
        self.user1.is_verified = True
        self.user1.save()
        self.user2 = User.objects.create_user(
            username="jim",
            email="jim@gmail.com",
            password="@Us3r.com"
        )
        self.user2.is_verified = True
        self.user2.save()

        self.new_article = {
                "article": {
                    "title": "How to train your dragon",
                    "description": "Ever wonder how?",
                    "body": "You have to believe"
                    }
                }

    def login(self, email, password):
        """
        Method to login users
        """
        return self.client.post(
            self.login_url,
            data=json.dumps({
                "user": {
                    "email": email,
                    "password": password
                }
            }))

    def is_authenticated(self, email, password):
        """Authenticate user
        """
        login_details = self.login(email, password)
        token = login_details.data['token']
        return self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)

    def create_article(self):
        """
        Create a new article
        """
        return self.client.post(self.create_url,
                                data=json.dumps(self.new_article))

    def get_all_articles(self):
        """
        Return all articles
        """
        return self.client.get(self.create_url)

    def get_one_article(self):
        """
        Return single article
        """
        return self.client.get(self.modify_url)
