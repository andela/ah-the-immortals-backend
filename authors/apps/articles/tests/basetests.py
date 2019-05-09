from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
import json
from authors.apps.articles.models import Article, Tag
from django.conf import settings

User = get_user_model()


class BaseTest(APITestCase):
    """
    Class to set up test case
    """

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("authentication:login")
        self.article_url = reverse("articles:article")
        self.articles_url = reverse("articles:articles", args=["this-is-mine"])
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
        return self.client.post(self.article_url,
                                data=json.dumps(self.new_article),
                                content_type="application/json")

    def get_all_articles(self):
        """
        Return all articles
        """
        return self.client.get(self.article_url)

    def get_one_article(self):
        """
        Return single article
        """
        self.create_article()
        return self.client.get(self.articles_url)

    def delete_article(self):
        """
        Delete one article
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.delete(self.articles_url)

    def update_article(self):
        """
        Update article
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.patch(self.articles_url,
                                 data=json.dumps(self.update),
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
        return self.client.patch(self.articles_url,
                                 data=json.dumps(self.update),
                                 content_type="application/json")

    def wrong_user_delete_article(self):
        """
        Wrong user delete article
        """
        self.other_user
        return self.client.delete(self.articles_url)


class TagsBaseTest(APITestCase):
    """
    Base Test for tags
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="mininguathor@gmail.com",
            username="mningauthor95",
            password="HeLV27@tica"
        )
        self.user.is_verified = True
        self.user.save()
        self.article = Article.objects.create(
            title="Talk Like TED",
            description="Tehcnology, Education and Design",
            body="To make your speech stand out you need to make it novel",
            author=self.user
        )
        self.articles_url = reverse("article:article")
        self.all_tags_url = reverse("article:all_tags")
        self.login_url = reverse("authentication:login")
        self.one_article_url = reverse(
            "articles:articles", args=[self.article.slug])
        self.update_url = reverse(
            "articles:articles", args=[self.article.slug])
        self.tagList = ["Analysis", "Principia"]
        self.update_tags = ["analytica", "cambridge"]
        self.article_data = {
            "title": "Infiniteness of Reals",
            "description": "Real Analysis",
            "body": "The infiniteness of reals",
            "tags": self.tagList
        }
        self.update_data = {
            "title": "Varying",
            "tags": self.update_tags
        }

    def clear_articles(self):
        """
        clears articles data from the database
        """
        [article.delete() for article in Article.objects.all()]

    def clear_tags(self):
        """
        Clears all tags from the database
        """
        [tag.delete() for tag in Tag.objects.all()]

    def login_user(self):
        response = self.client.post(
            path=self.login_url,
            data={
                "email": self.user.email,
                "password": "HeLV27@tica"
            },
            format='json'
        )
        return response.data

    def authenticate_user(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer '+self.login_user().get("token"))

    def post_article_with_tags(self):
        """
        A method for posting an article with tags
        """
        response = self.client.post(
            path=self.articles_url,
            data=self.article_data,
            format='json'
        )
        return response

    def create_article_with_tags(self):
        """
        Successfully creates article with tags
        """
        self.authenticate_user()
        response = self.post_article_with_tags()
        return response

    def get_articles(self):
        """
        Gets tags for articles
        """
        response = self.client.get(
            path=self.articles_url,
            format='json'
        )
        return response

    def get_all_tags(self):
        """
        Fetches all articles
        """
        response = self.client.get(
            path=self.all_tags_url,
            format='json'
        )
        return response

    def update_article(self):
        """
        Updates an article
        """
        self.authenticate_user()
        response = self.client.patch(
            path=self.update_url,
            data=self.update_data,
            format='json'
        )
        return response

    def fetch_one_article(self):
        response = self.client.get(
            path=self.update_url,
            format='json'
        )
        return response


class PagniationBaseTest(APITestCase):
    """
    Base test for paginated article data
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="mininguathor@gmail.com",
            username="mningauthor95",
            password="HeLV27@tica"
        )
        self.user.is_verified = True
        self.user.save()
        self.default_page_limit = 10
        self.page = 1
        self.page_url_prefix = settings.DOMAIN+'/api/articles/'
        self.get_articles_url = reverse("article:article")
        self.path = ""
        self.error_msg = "Invalid page limit"

    def generate_articles(self):
        """
        Generates 20 articles
        """
        for i in range(21):
             Article.objects.create(
                 title="Talk Like TED",
                 description="Tehcnology, Education and Design",
                 body="To make your speech stand out you need to make it novel",
                 author=self.user
             )

    def get_articles_per_page(self, page=1, page_limit=None):
        """
        Gets paginated response with a limit and a page
        """
        self.path = self.page_url_prefix+'?page=' + \
            str(page)+'&page_limit='+str(page_limit)
        response = self.client.get(
            path=self.path,
            format="json"
        )
        return response

    def get_articles(self):
        """
        Gets articles using defaults
        """
        response = self.client.get(
            path=self.get_articles_url,
            format='json'
        )
        return response

    def get_next_page(self):
        """
        Gets next page
        """
        self.path = self.get_articles().data.get("next")
        response = self.client.get(
            path=self.path,
            format='json'
        )
        return response

    def get_previous_page(self):
        """
        Gets previous page
        """
        self.path = self.get_next_page().data.get("previous")
        response = self.client.get(
            path=self.path,
            format='json'
        )
        return response
