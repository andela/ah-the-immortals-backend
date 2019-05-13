import json

from rest_framework.views import status
from .basetests import BaseTest


class RatingArticlesTest(BaseTest):
    """
    Test cases for article ratings
    """
    unauthorized = "Authentication credentials were not provided."

    def test_rate_an_article_with_authorized_user(self):
        """
        Test if an article is rated when no data is passed
        """
        rating = self.rate_article()
        self.assertEqual(rating.status_code, status.HTTP_201_CREATED)

    def test_update_ratings_on_an_article_with_authorized_user(self):
        """
        Test if an article is rated when no data is passed
        """
        rating = self.update_rate_article()
        self.assertEqual(rating.status_code, status.HTTP_201_CREATED)


    def test_rate_an_article_with_greater_than_five(self):
        """
        Test if an article is rated when the rate is more that 5
        """
        rating = self.rate_article_more_than_five()
        self.assertEqual(rating.status_code, status.HTTP_400_BAD_REQUEST)


    def test_rate_an_article_with_less_than_one(self):
        """
        Test if an article is rated when that rate is less than 1
        """
        rating = self.rate_article_less_than_one()
        self.assertEqual(rating.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_a_non_existing_article(self):
        """
        Test if an article is rated when article doesn't exist
        """

        rating = self.rate_non_existing_article()
        self.assertEqual(rating.status_code, status.HTTP_404_NOT_FOUND)

    def test_rate_own_article(self):
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        rating = self.rate_article()
        self.assertEqual(rating.data.get("errors").get("error"), "You can't rate your own article")
