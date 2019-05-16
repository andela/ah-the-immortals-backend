from .basetests import BaseTest
from rest_framework import status


class TestReadTime(BaseTest):
    """
    Tests read time of an aerticle
    """

    def setUp(self):
        super().setUp()
        self.new_article["body"] = self.word_generator(795)
        self.minutes_time = "3 minutes"
        self.seconds_time = "3 seconds"

    def word_generator(self, num_words):
        """
        Generates a given number of words
        """
        words = ""
        for i in range(num_words):
            words += "random "
        return words

    def test_article_post_read_time(self):
        """
        Tests read time of an article during post
        """
        response = self.create_article()
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            response.data.get("readtime"),
            self.minutes_time
        )

    def test_article_update_read_time(self):
        """
        Tests read time of an article during an update
        """
        response = self.update_article()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data.get("article").get("readtime"),
            self.seconds_time
        )

    def test_single_article_read_time(self):
        """
        Tests article read time for a single article
        """
        response = self.get_one_article()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data.get("article").get("readtime"),
            self.seconds_time
        )

    def test_get_all_articles_read_time(self):
        """
        Test article read time on all articles
        """
        response = self.get_all_articles()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data.get("results").get("articles")[0].get("readtime"),
            self.seconds_time
        )
