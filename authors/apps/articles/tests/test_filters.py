from authors.apps.articles.tests.basetests import FilterBaseTest
from authors.apps.articles.filters import ArticleFilter
from rest_framework import status


class TestFilters(FilterBaseTest):
    """
    Tests searching and filtering
    """

    def test_filter_by_author(self):
        """
        tests searching for articles by author's name
        """
        self.create_an_article()
        response = self.filter_by_author()
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK
                         )

    def test_filter_non_author(self):
        """
        tests filtering for articles by non author's name
        """
        self.create_an_article()
        response = self.filter_by_non_author()
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND
                         )
        message = response.data.get("error")
        self.assertEqual(message, 'We couldn’t find any articles')

    def test_filter_by_one_tag(self):
        """
        tests filtering for articles by tag
        """
        self.create_an_article()
        response = self.filter_by_tag()
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK
                         )

    def test_filter_by_title(self):
        """
        tests filtering for articles by tag
        """
        self.create_an_article()
        response = self.filter_title()
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK
                         )

    def test_filter_by_two_tags(self):
        """
        tests filtering for articles by tag two tags
        """
        self.create_an_article()
        response = self.filter_by_two_tags()
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK
                         )

    def test_filter_by_title_and_tags(self):
        """
        tests search for articles by title
        """
        self.create_an_article()
        response = self.filter_by_tag_and_title()
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK
                         )
