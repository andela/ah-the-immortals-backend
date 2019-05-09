from authors.apps.articles.tests.basetests import PagniationBaseTest
from rest_framework import status


class TestPagination(PagniationBaseTest):
    """
    Tests paginated article responses
    """

    def setUp(self):
        super().setUp()
        self.generate_articles()

    def test_get_articles_with_defaults(self):
        """
        Tests getting of articles with defaults
        """
        response = self.get_articles()
        data = response.data.get("results").get("articles")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(data),
            self.default_page_limit
        )

    def test_variable_page_limit(self):
        """
        Tests variable page limit for pagination
        """
        response = self.get_articles_per_page(page_limit=10)
        data = response.data.get("results").get("articles")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(data),
            10
        )

    def test_next_page_existance(self):
        """
        Tests existence of next page
        """
        response = self.get_next_page()
        data = response.data.get("results").get("articles")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(data),
            self.default_page_limit
        )

    def test_get_previous_page(self):
        response = self.get_previous_page()
        data = response.data.get("results").get("articles")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(data),
            self.default_page_limit
        )

    def test_invalid_page_number(self):
        """
        Tests invalid page number
        """
        response = self.get_articles_per_page(page=15, page_limit=10)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            response.data.get("detail"),
            "Invalid page."
        )
