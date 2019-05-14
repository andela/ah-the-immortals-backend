import json

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
import json
from authors.apps.articles.models import Article, Tag, Comment
from django.conf import settings
from authors.apps.articles.filters import ArticleFilter

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
        self.comments_url = reverse("articles:comment", args=["this-is-mine"])
        self.comments_url_fail = reverse(
            "articles:comment", args=["nof"])
        self.commentsdetail_url = reverse(
            "articles:commentdetail", args=["this-is-mine", 877777])
        self.commentsdetail_url_delete = reverse(
            "articles:commentdetail", args=["this-is-mine", 1])
        self.comments_url_not_found = reverse(
            "articles:comment", args=["not-found"])
        self.commentsdetail_url_one_comment = reverse(
            "articles:commentdetail", args=["this-is-mine", 18])

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
        self.comment = Comment.objects.create(
            article=self.article,
            author=self.user1,
            body='this is a test body'
        )
        self.comment.save()
        self.update = {
            "description": "Brian Koin is making noise"
        }
        self.update_comment = {
            "body": "this is a test update"
        }
        self.new_comment = {
            "body": "this is another test comment"
        }
        self.new_child_comment = {
            "body": "this is a child test comment"
        }
        self.user = self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.other_user = self.is_authenticated("jim@gmail.com", "@Us3r.com")
        self.comment = {
            "body": "This is a test comment"
        }
        self.maxDiff = None

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
        """if
        Create a new article
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
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
        Updacommentthat does not exist
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

    def like_dislike_article(self, vote_type):
        """
        Like an article
        """
        slug = str(self.article.slug)
        url = reverse("articles:likes", args=[slug, vote_type])
        return self.client.post(
            url,
            content_type="application/json"
        )

    def like_dislike_article_noslug(self, vote_type):
        """
        Like an article
        """
        slug = "ilove-this"
        url = reverse("articles:likes", args=[slug, vote_type])
        return self.client.post(
            url,
            content_type="application/json"
        )

    def delete_like(self, vote_type):
        """
        Like and Unlike
        """
        slug = str(self.article.slug)
        url = reverse("articles:likes", args=[slug, vote_type])
        return self.client.delete(
            url,
            content_type="application/json"
        )
        
    def delete_dislike(self, vote_type):
        """
        Like and Unlike
        """
        slug = str(self.article.slug)
        url = reverse("articles:likes", args=[slug, vote_type])
        return self.client.delete(
            url,
            content_type="application/json"
        )

    def delete_like_dislike_noslug(self, vote_type):
        """
        Delete while slug is wrong
        """
        slug = "i-love-this"
        url = reverse("articles:likes", args=[slug, vote_type])
        return self.client.delete(
            url,
            content_type="application/json"
        )

    def get_token(self):
        """
        Method to generate token
        """
        user = self.user1
        token, created = Token.objects.get_or_create(user=user)
        token = token.key
        return token

    def post_favorite(self):
        """
        A method to favorite an article
        """
        slug = str(self.article.slug)
        url = reverse("articles:favorite", args=[slug])
        return self.client.post(
            url,
            data=json.dumps(
                {
                    "article": self.article.id,
                    "user": self.user1.id
                }
            ),
            content_type="application/json")
        return self.client.post(url)

    def post_comment(self):
        """
        Method to post comments
        """
        slug = str(self.article.slug)
        url = reverse("articles:comment", args=[slug])
        return self.client.post(
            url, self.comment
        )

    def post_favorite_slug_doesnotexist(self):
        """
        A method to favorite an article
        """
        slug = "i-love-this"
        url = reverse("article:favorite", args=[slug])
        return self.client.post(
            url,
            data=json.dumps(
                {
                    "article": self.article.id,
                    "user": self.user1.id
                }
            ),
            content_type="application/json"
        )

    def delete_favorite(self):
        """
        A method to remove articles from favorites
        """

        slug = str(self.article.slug)
        url = reverse("articles:favorite", args=[slug])
        return self.client.delete(
            url,
            content_type="application/json"
        )

    def delete_favorite_invalidslug(self):
        """
        A method to favorite an article
        """
        slug = "i-love-this"
        url = reverse("articles:favorite", args=[slug])
        return self.client.delete(
            url,
            content_type="application/json"
        )

    def get_favorites(self):
        """
        A method to get all user favorite articles
        """
        url = reverse("articles:get_favorite")
        return self.client.get(
            url,
            content_type="application/json"
        )
        return self.client.get(url)

    def create_comment(self):
        """if
        Create a new comment
        """
        self.user
        return self.client.post(self.comments_url,
                                data=json.dumps(self.new_comment),
                                content_type="application/json")

    def create_comment_fail(self):
        """if
        Create a new comment
        """
        self.user
        return self.client.post(self.comments_url_fail,
                                data=json.dumps(self.new_comment),
                                content_type="application/json")

    def get_all_comments(self):
        """
        Return all comments
        """
        self.user
        return self.client.get(self.comments_url)

    def get_one_comment(self):
        """
        Return all comments
        """
        self.user
        return self.client.get(self.commentsdetail_url_delete)

    def delete_comment(self):
        """
        Delete a comment unsuccefully
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.delete(self.commentsdetail_url)

    def update_comment_unsuccefully(self):
        """if
        Create a new comment
        """
        commentsdetail_url_delete = reverse(
            "articles:commentdetail", args=["this-is-mine", 998989])

        self.user
        return self.client.post(commentsdetail_url_delete,
                                data=json.dumps(self.update_comment),
                                content_type="application/json")

    def rate_article(self):
        """
        Pass slug to the url and post the ratings
        """
        slug = str(self.article.slug)
        url = reverse("articles:rating_articles", args=[slug])
        return self.client.post(
            url,
            data=json.dumps({
                "rate": 4
            }),
            content_type="application/json"
        )

    def update_rate_article(self):
        """
        Pass slug to the url and post the ratings
        """
        slug = str(self.article.slug)
        url = reverse("articles:rating_articles", args=[slug])
        return self.client.post(
            url,
            data=json.dumps({
                "rate": 3
            }),
            content_type="application/json"
        )

    def rate_article_more_than_five(self):
        """
        Pass slug to the url and post the ratings
        """
        slug = str(self.article.slug)
        url = reverse("articles:rating_articles", args=[slug])
        return self.client.post(
            url,
            data=json.dumps({
                "rate": 7
            }),
            content_type="application/json"
        )

    def rate_article_less_than_one(self):
        """
        Pass slug to the url and post the ratings
        """
        slug = str(self.article.slug)
        url = reverse("articles:rating_articles", args=[slug])
        return self.client.post(
            url,
            data=json.dumps({
                "rate": -1
            }),
            content_type="application/json"
        )

    def rate_non_existing_article(self):
        """
        Pass slug to the url and post the ratings
        """
        slug = "how-to-let-go"
        url = reverse("articles:rating_articles", args=[slug])
        return self.client.post(
            url,
            data=json.dumps({
                "rate": 4
            }),
            content_type="application/json")

    def create_comment(self):
        """if
        Create a new comment
        """
        self.user
        return self.client.post(self.comments_url,
                                data=json.dumps(self.new_comment),
                                content_type="application/json")

    def create_child_comment(self):
        """if
        Create a new child comment
        """
        self.user
        parent_comment = self.create_comment()
        id = parent_comment.data['id']
        return self.client.post(reverse(
            "articles:commentdetail", args=["this-is-mine", id]),
            data=json.dumps(self.new_comment),
            content_type="application/json")

    def create_child_comment_not_found(self):
        """if
        Create a new child comment
        """
        self.user
        self.create_comment()
        return self.client.post(self.commentsdetail_url_delete,
                                data=json.dumps(self.new_comment),
                                content_type="application/json")

    def create_comment_fail(self):
        """if
        Create a new comment
        """
        self.user
        return self.client.post(self.comments_url_fail,
                                data=json.dumps(self.new_comment),
                                content_type="application/json")

    def get_all_comments(self):
        """
        Return all comments
        """
        self.user
        return self.client.get(self.comments_url)

    def get_comments_by_id(self):
        """
        Return  comments by id
        """
        self.user
        return self.client.get(self.commentsdetail_url_one_comment)

    def get_one_comment(self):
        """
        Return one comment
        """
        self.user
        return self.client.get(self.commentsdetail_url_delete)

    def get_one_comment_not_found(self):
        """
        Return not found comment
        """
        self.user
        return self.client.get(self.comments_url_not_found)

    def delete_comment(self):
        """
        Delete a comment unsuccefully
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.delete(self.commentsdetail_url)

    def update_comment_unsuccefully(self):
        """if
        Create a new comment
        """
        commentsdetail_url_delete = reverse(
            "articles:commentdetail", args=["this-is-mine", 998989])

        self.user
        return self.client.put(commentsdetail_url_delete,
                               data=json.dumps(self.update_comment),
                               content_type="application/json")

    def update_comment_succefully(self):
        """if
        update a comment
        """
        parent_comment = self.create_comment()
        id = parent_comment.data['id']
        return self.client.put(reverse(
            "articles:commentdetail", args=["this-is-mine", id]),
            data=json.dumps(self.update_comment),
            content_type="application/json")

    def delete_comment_succefully(self):
        """if
        update a comment
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        parent_comment = self.create_comment()
        id = parent_comment.data['id']
        return self.client.delete(reverse(
            "articles:commentdetail", args=["this-is-mine", id]),
        )

    def get_comment_by_id(self):
        """if
        update a comment
        """
        parent_comment = self.create_comment()
        id = parent_comment.data['id']
        return self.client.get(reverse(
            "articles:commentdetail", args=["this-is-mine", id]))


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
        self.tagList = ["Analysis", "Principia"]
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


class FilterBaseTest(TagsBaseTest):
    def setUp(self):
        super().setUp()
        self.tag_objects = []
        for name in self.tagList:
            tag = Tag.objects.create(tag_name=name)
            self.tag_objects.append(tag)
        self.article = Article.objects.create(
            title="Talk Like TED",
            description="Tehcnology, Education and Design",
            body="To make your speech stand out you need to make it novel",
            author=self.user
        )
        for tag in self.tag_objects:
            self.article.tags.add(tag)

    def post_an_article(self):
        """
        A method for posting an article
        """
        response = self.client.post(
            path=self.articles_url,
            data=self.article_data,
            format='json'
        )
        return response

    def create_an_article(self):
        """
        method to creates article
        """
        self.authenticate_user()
        response = self.post_an_article()
        return response

    def filter_by_author(self):
        """
        Filter by author
        """
        response = self.client.get((self.articles_url)
                                   + '?author=' + 'mningauthor95',
                                   format='json'
                                   )
        return response

    def filter_by_non_author(self):
        """
        Filter by author
        """
        response = self.client.get((self.articles_url)
                                   + '?author=' + 'philip',
                                   format='json'
                                   )
        return response

    def filter_by_tag(self):
        """
        Filter by tag
        """
        response = self.client.get((self.articles_url)
                                   + '?tags=' + 'Analysis',
                                   format='json'
                                   )
        return response

    def filter_by_title(self):
        """
        Filter by title
        """
        response = self.client.get((self.articles_url)
                                   + '?title=' + 'TED',
                                   format='json'
                                   )
        return response

    def filter_by_two_tags(self):
        """
        Filter by two tags
        """
        response = self.client.get((self.articles_url)
                                   + '?tags=' + 'Analysis' + ',' + 'Principia',
                                   format='json'
                                   )
        return response

    def filter_title(self):
        """
        Filter by two tags
        """
        response = self.client.get((self.articles_url)
                                   + '?title=' + 'ted',
                                   format='json'
                                   )
        return response

    def filter_by_tag_and_title(self):
        """
        Filter by tag
        """
        response = self.client.get((self.articles_url)
                                   + '?tags=' + 'Analysis' + '?title=' + 'TED',
                                   format='json'
                                   )
        return response

    def filter_by_author_and_title(self):
        """
        Filter by tag
        """
        response = self.client.get((self.articles_url)
                                   + '?author=' + 'philip' + '?title=' + 'ted',
                                   format='json'
                                   )
        return response
