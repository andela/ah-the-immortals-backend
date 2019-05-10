from rest_framework import status

from authors.apps.articles.tests.basetests import BaseTest


class TestFavoriteArticle(BaseTest):
    """
    Tests for favoriting articles
    """

    def test_favorite_successfuly(self):
        """
        Test method for successfully favoriting an article
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.post_favorite()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("message"),
                         "Article added to favorites")

    def test_favorite_invalid_slug(self):
        """
        Test method for invalid slug
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.post_favorite_slug_doesnotexist()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Article does not exist")

    def test_already_favorited(self):
        """
        Test method for already favorited article
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.post_favorite()
        response = self.post_favorite()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("errors").get(
            "exist")[0], "Already favorited this article")

    def test_delete_favorite_successfully(self):
        """
        Test method for successfully deleting favorites
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.post_favorite()
        response = self.delete_favorite()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"),
                         "Article removed from favorites")

    def test_delete_favorite_notfavorited(self):
        """
        Test method for successfully deleting favorites
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.delete_favorite()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("errors").get("exist")[
                         0], "You have not favorited this article")

    def test_get_favorite_successfully(self):
        """
        Test method for successfully deleting favorites
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.post_favorite()
        response = self.get_favorites()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("favorites")[
                         0].get("slug"), self.article.slug)

    def test_delete_favorite_invalidslug(self):
        """
        Test method for successfully deleting favorites
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.delete_favorite_invalidslug()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Article does not exist")
