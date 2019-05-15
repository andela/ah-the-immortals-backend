import json
from rest_framework import status

from authors.apps.articles.models import Bookmarks

from .basetests import BaseTest


class TestBookmarks(BaseTest):
    """
    Class to test bookmarking
    """

    def test_bookmark_successful(self):
        """
        Test to bookmark successfully
        """
        response = self.create_bookmark()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(len(response.data), 1)

    def test_article_has_been_bookmarked(self):
        """
        Test article has been bookmarked
        """
        response = self.create_bookmark_already()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('Article has been bookmarked',
                         response.data['message'])

    def test_bookmark_does_not_exist(self):
        """
        Test bookmarks not found
        """
        response = self.get_bookmarks_not_found()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual('Bookmarks not found', response.data['message'])

    def test_remove_an_article_from_bookmarks(self):
        """
        Remove an article from bookmarks
        """
        response = self.remove_bookmark_succefully()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("Bookmark has been removed", response.data['message'])

    def test_remove_bookmark_unsuccefully(self):
        """
        Test remove bookmark not found
        """
        response = self.remove_bookmark_unsuccefully()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual("Bookmark not found", response.data['detail'])

    def test_article_does_not_exist(self):
        """
        Test article not found
        """
        response = self.create_bookmark_not_found()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual("Article does not exist", response.data['detail'])

    def test_get_all_bookmarks(self):
        """
        Test get all bookmarks
        """
        response = self.get_all_bookmarks()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['articles'])
