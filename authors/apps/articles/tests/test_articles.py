from rest_framework import status
from .basetests import BaseTest


class TestArticles(BaseTest):
    """
    Class to test articles CRUD
    """
    slug = "how-to-train-your-dragon"
    slug2 = "this-is-mine"
    description = "I do not want it"
    updated = "Brian Koin is making noise"
    msg = "Article deleted"
    error = "Article does not exist"
    unauthorized = "Cannot edit an article that is not yours"
    forbidden = "Cannot delete an article that is not yours"

    def test_successful_article_creation(self):
        """
        Test successful creation of an article
        """
        response = self.create_article()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("slug"), self.slug)

    def test_successful_get_all_articles(self):
        """
        Test get all articles
        """
        response = self.get_all_articles()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results").get("articles")[0].get("slug"),
                         self.slug2)

    def test_successful_get_one_article(self):
        """
        Test get one article
        """
        response = self.get_one_article()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("article").get("description"),
                         self.description)

    def test_successful_update_article(self):
        """
        Test update one article
        """
        response = self.update_article()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("article").get("description"),
                         self.updated)

    def test_successful_delete_article(self):
        """
        Test delete article
        """
        response = self.delete_article()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], self.msg)

    def test_update_nonexistent_article(self):
        """
        Test update an article that does not exist
        """
        response = self.update_nonexistent_article()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], self.error)

    def test_delete_nonexistent_article(self):
        """
        Test delete an article that does not exist
        """
        response = self.delete_nonexistent_article()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], self.error)

    def test_wrong_user_update_article(self):
        """
        Test wrong user update article
        """
        response = self.wrong_user_update_article()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("errors").get("error")[0],
                         self.unauthorized)

    def test_wrong_user_delete_article(self):
        """
        Test wrong user delete article
        """
        response = self.wrong_user_delete_article()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("errors").get("error")[0],
                         self.forbidden)
