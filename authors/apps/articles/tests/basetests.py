from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
from ..models import Article
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
        self.modify_url = reverse("articles:articles", args=["this-is-mine"])
        self.nonexistent_url = reverse("articles:articles", args=["not-found"])

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
                    "title": "How to train your dragon",
                    "description": "Ever wonder how?",
                    "body": "You have to believe"
                }
        self.article = Article.objects.create(
            title='this is mine',
            description='I do not want it',
            body='what is the purpose of body',
            author=self.user1,
            image='image/upload/v1557052449/tt30hqlfc3eaflfqtobo.jpg'
        )
        self.article.save()
        self.update = {
                "description": "Brian Koin is making noise"
        }
        self.user = self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.other_user = self.is_authenticated("jim@gmail.com", "@Us3r.com")

    def login(self, email, password):
        """
        Method to login users
        """
        return self.client.post(
            self.login_url,
            data=json.dumps({
                    "email": email,
                    "password": password
            }), content_type="application/json")

    def is_authenticated(self, email, password):
        """
        Authenticate user
        """
        login_details = self.login(email, password)
        token = login_details.data['token']
        return self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)

    def create_article(self):
        """
        Create a new article
        """
        self.user
        return self.client.post(self.create_url,
                                data=json.dumps(self.new_article),
                                content_type="application/json")

    def get_all_articles(self):
        """
        Return all articles
        """
        return self.client.get(self.create_url)

    def get_one_article(self):
        """
        Return single article
        """
        self.create_article()
        return self.client.get(self.modify_url)

    def delete_article(self):
        """
        Delete one article
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.delete(self.modify_url)

    def update_article(self):
        """
        Update article
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.patch(self.modify_url, data=json.dumps(self.update),
                                 content_type="application/json")

    def update_nonexistent_article(self):
        """
        Update an article that does not exist
        """
        self.user
        return self.client.patch(self.nonexistent_url,
                                 data=json.dumps(self.update),
                                 content_type="application/json")

    def delete_nonexistent_article(self):
        """
        Delete an article that does not exist
        """
        self.user
        return self.client.delete(self.nonexistent_url)

    def wrong_user_update_article(self):
        """
        Wrong user update article
        """
        self.other_user
        return self.client.patch(self.modify_url, data=json.dumps(self.update),
                                 content_type="application/json")

    def wrong_user_delete_article(self):
        """
        Wrong user delete article
        """
        self.other_user
        return self.client.delete(self.modify_url)
