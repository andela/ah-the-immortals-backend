import json

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token

from authors.apps.escalation.models import EscalationModel
from authors.apps.articles.models import Article
from django.conf import settings


User = get_user_model()


class BaseTest(APITestCase):
    """
    Class to set up test case
    """

    def setUp(self):
        """
        Setting up the client
        """
        self.client = APIClient()
        self.login_url = reverse("authentication:login")
        self.article_url = reverse("articles:article")

        self.user1 = User.objects.create_user(
            username="Pablo",
            email="Escobar@pablo.com",
            password="@Us3r.com"
        )
        self.user1.is_verified = True
        self.user1.save()

        self.user2 = User.objects.create_user(
            username="Emirry",
            email="ess@rry.com",
            password="@Us3r.com"
        )
        self.user2.is_verified = True
        self.user2.save()

        self.user3 = User.objects.create_user(
            username="Mercy",
            email="mercy@hope.com",
            password="@Us3r.com"
        )
        self.user3.is_verified = True
        self.user3.is_staff = True
        self.user3.save()

        self.new_article = {
            "title": "How to train your dragon",
            "description": "Ever wonder how?",
            "body": "You have to believe"
        }

        self.article = Article.objects.create(
            title='this is mine',
            description='I do not want it',
            body='what is the purpose of body',
            author=self.user2,
            image='image/upload/v1557052449/tt30hqlfc3eaflfqtobo.jpg'
        )
        self.article.save()

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
        token = self.user2.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        return self.client.post(self.article_url,
                                data=json.dumps(self.new_article),
                                content_type="application/json")

    def escalate_an_article(self):
        """
        Report an article that doesn't exist
        """
        slug = "how-to-help"
        url = reverse("escalation:escalate", args=[slug])
        response = self.client.post(
            url,
            data=json.dumps({
                "reason": "Rule Violation",
                "description": "He broke some rules"
            }),
            content_type="application/json"
        )
        return response

    def escalate_an_article_successfully(self):
        """
        Report an article successfully
        """
        slug = str(self.article.slug)
        url = reverse("escalation:escalate", args=[slug])
        response = self.client.post(
            url,
            data=json.dumps({
                "reason": "Rule Violation",
                "description": "He broke some rules"
            }),
            content_type="application/json"
        )
        return response

    def escalate_an_article_twice(self):
        """
        Try and report an article twice
        """
        slug = str(self.article.slug)
        url = reverse("escalation:escalate", args=[slug])
        self.client.post(
            url,
            data=json.dumps({
                "reason": "Rule Violation",
                "description": "He broke some rules"
            }),
            content_type="application/json"
        )
        return self.client.post(
            url,
            data=json.dumps({
                "reason": "Rule Violation",
                "description": "He broke some rules"
            }),
            content_type="application/json"
        )

    def update_an_escalated_article(self):
        """
        Update an eslation
        """
        slug = str(self.article.slug)
        url = reverse("escalation:escalate", args=[slug])
        self.client.post(
            url,
            data=json.dumps({
                "reason": "Rule Violation",
                "description": "He broke some rules"
            }),
            content_type="application/json"
        )
        return self.client.post(
            url,
            data=json.dumps({
                "reason": "Rule Violation",
                "description": "He broke some rules, he posted someone else work and pasted as his"
            }),
            content_type="application/json"
        )

    def delete_article(self):
        """
        Try and delete an article
        """
        slug = str(self.article.slug)
        url = reverse("escalation:escalate", args=[slug])
        return self.client.delete(
            url,
            content_type="application/json"
        )

    def get_article(self):
        """
        Try and get an article
        """
        url = reverse("escalation:get_escalate")
        return self.client.get(
            url,
            content_type="application/json"
        )
