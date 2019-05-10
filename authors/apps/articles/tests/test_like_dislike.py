from rest_framework import status

from .basetests import BaseTest


class TestLikeDislike(BaseTest):
    """
    A class to test likes and dislikes
    """

    def test_liking_successfully(self):
        """
        Tests for liking an article
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.like_dislike_article("like")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"),
                         "Like posted successfully")

    def test_disliking_successfully(self):
        """
        Tests for disliking an article
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.like_dislike_article("dislike")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"),
                         "Dislike posted successfully")

    def test_like_dislike_noslug(self):
        """
        Test for slug does not exist
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.like_dislike_article_noslug("like")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Article does not exist")

    def test_wrong_verb_like_dislike(self):
        """
        Test for wrong verb like or dislike
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.like_dislike_article("dlike")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("errors").get("vote_verb")[
                         0], "Vote verb specified does not exist")

    def test_delete_like_dislike(self):
        """
        Test for deleting likes and dislikes
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.like_dislike_article("like")
        response = self.delete_like_dislike("dislike")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message")[
                         0], "Vote delete successfully")

    def test_delete_likes_dislikes_no_slug(self):
        """
        Tests for deleting while no slug
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.delete_like_dislike_noslug("dislike")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Article does not exist")

    def test_delete_likes_dislikes_twice(self):
        """
        Test for unliking/disliking an article twice
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.like_dislike_article("like")
        self.delete_like_dislike("dislike")
        response = self.delete_like_dislike("dislike")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("errors").get(
            "error"), "You have not liked/disliked this article")
