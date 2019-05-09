from authors.apps.articles.tests.basetests import TagsBaseTest
from authors.apps.articles.models import Tag, Article
from rest_framework import status


class TestTagsModel(TagsBaseTest):
    """
    Tests tags models
    """

    def setUp(self):
        super().setUp()
        self.tag = Tag.objects.create(tag_name="Novel")

    def test_data_persistence(self):
        """
        Tests persistence of data in the database
        """
        tag = Tag.objects.get(tag_name="Novel")
        self.assertEqual(
            Tag.objects.all().count(),
            1
        )
        self.assertEqual(
            tag.tag_name,
            "Novel"
        )

    def test_many_articles_against_one_tag(self):
        """
        Tests if one tag can be used for many articles
        """
        self.article2 = Article.objects.create(
            title="The Gods of Gabatula",
            description="Short Stories",
            body="Once upon a time,...",
            author=self.user
        )
        self.article.tags.add(self.tag)
        self.article2.tags.add(self.tag)
        self.assertEqual(
            self.tag.articles.count(),
            2
        )

    def test_many_tags_agains_one_article(self):
        """
        Tests many tags added agains one article
        """
        self.tag2 = Tag.objects.create(tag_name="technology")
        self.article.tags.add(self.tag)
        self.article.tags.add(self.tag2)
        self.assertEqual(
            self.article.tags.all().count(),
            2
        )

    def test_tag_string_representation(self):
        """
        Tests string representation of a tag
        """
        self.assertEqual(
            str(self.tag),
            "Novel"
        )


class TestPostTags(TagsBaseTest):
    """
    Tests post tags endpoint
    """

    def setUp(self):
        super().setUp()

    def test_post_by_unauthenticated_user(self):
        """
        Tests adding of tags by unauthenticated user
        """
        response = self.post_article_with_tags()
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            response.data.get("detail"),
            "Authentication credentials were not provided."
        )

    def test_successful_adding_of_tags(self):
        """
        Tests adding of tags to articles by authenticated users
        """
        response = self.create_article_with_tags()
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            response.data.get("tagList"),
            self.tagList
        )

    def test_tag_redanduncy(self):
        """
        Tests if tags could be redandunt in the databse
        """
        self.create_article_with_tags()
        response = self.create_article_with_tags()
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            response.data.get("tagList"),
            self.tagList
        )

    def test_tags_on_get_all_articles(self):
        """
        Tests return of articles on get all articles endpoint
        """
        self.clear_articles()
        self.create_article_with_tags()
        response = self.get_articles()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data.get("results").get("articles")[0].get("tagList"),
            self.tagList
        )


class TestGetTags(TagsBaseTest):
    """
    Tests fetching of all tags from database
    """

    def setUp(self):
        super().setUp()
        self.clear_tags()

    def test_missing_tags(self):
        """
        Tests missing tags
        """
        response = self.get_all_tags()
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            response.data.get("errors").get("tags")[0],
            "There are no tags in Authors Heaven at the moment"
        )

    def test_successful_fetch_of_all_tags(self):
        """
        Tests fetching of all tags from database
        """
        self.create_article_with_tags()
        response = self.get_all_tags()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data.get("tags"),
            self.tagList
        )


class TestUpdateTags(TagsBaseTest):
    """
    Tests update of tags
    """

    def setUp(self):
        super().setUp()
        for tag in self.tagList:
            tag_object = Tag.objects.create(
                tag_name=tag
            )
            self.article.tags.add(tag_object)

    def test_removal_of_tags(self):
        """
        Tests removal of tags from an article during update
        """
        response = self.update_article()
        self.assertEqual(
            response.data.get("article").get("tagList"),
            self.update_tags
        )
        self.assertNotEqual(
            response.data.get("tagList"),
            self.tagList
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_maintaining_original_tags(self):
        """
        Tests update of of article without tags
        """
        del self.update_data["tags"]
        response = self.update_article()
        self.assertEqual(
            response.data.get("article").get("tagList"),
            self.tagList
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


class TestFetchOneArticle(TestUpdateTags):
    """
    Tests fetching of a tags on a single article
    """

    def setUp(self):
        super().setUp()

    def test_zero_tags(self):
        """
        Tests fetching of a single article without a tags
        """
        self.clear_tags()
        response = self.fetch_one_article()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data.get("article").get("tagList"),
            []
        )

    def test_article_with_tags(self):
        """
        Tests an arrticle with tags
        """
        response = self.fetch_one_article()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data.get("article").get("tagList"),
            self.tagList
        )
