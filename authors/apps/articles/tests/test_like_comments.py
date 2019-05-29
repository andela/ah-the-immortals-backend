import json
from rest_framework import status
from authors.apps.articles.models import LikeDislikeComment
from .basetests import LikeCommentsBaseTests


class TestLikeComment(LikeCommentsBaseTests):
    """
    Test suite for liking a comment feature
    """

    def setUp(self):
        super().setUp()
        self.client.credentials()
        self.unauthenticated_msg =\
            "Authentication credentials were not provided."
        self.unexisting_comment_msg = "comment does not exist"

    def test_like_when_unauthenticated(self):
        """
        Tests liking of comment when not authenticated
        """
        response = self.like()
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            response.data.get("detail"),
            self.unauthenticated_msg
        )

    def test_dislike_when_unauthenticated(self):
        """
        Tests disliking of a comment when not authenticated
        """
        response = self.dislike()
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            response.data.get("detail"),
            self.unauthenticated_msg
        )

    def test_successful_comment_like(self):
        """
        Tests successful liking of a comment
        """
        response = self.like_comment()
        data = response.data.get("comment").get("likes_info")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            data.get("likes_count"),
            1
        )
        self.assertEqual(
            data.get("like"),
            True
        )
        self.assertEqual(
            data.get("dislikes_count"),
            0
        )
        self.assertEqual(
            data.get("dislike"),
            False
        )
        self.assertEqual(
            response.data.get("message"),
            "Comment liked"
        )

    def test_successful_comment_dislike(self):
        """
        Tests successful comment dislike
        """
        response = self.dislike_comment()
        data = response.data.get("comment").get("likes_info")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            data.get("likes_count"),
            0
        )
        self.assertEqual(
            data.get("like"),
            False
        )
        self.assertEqual(
            data.get("dislikes_count"),
            1
        )
        self.assertEqual(
            data.get("dislike"),
            True
        )
        self.assertEqual(
            response.data.get("message"),
            "Comment disliked"
        )

    def test_liking_unexisting_comment(self):
        """
        Tests liking of unexisting comment
        """
        response = self.like_unexisting_comment()
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            response.data.get("message"),
            self.unexisting_comment_msg
        )

    def test_disliking_unexisting_comment(self):
        """
        Tests disliking of unexisting comment
        """
        response = self.dislike_unexisting_comment()
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            response.data.get("message"),
            self.unexisting_comment_msg
        )

    def test_dislking_comment_more_than_once(self):
        """
        Tests disliking of a comment more than once
        """
        response = self.dislike_a_comment_more_than_once()
        data = response.data.get("comment").get("likes_info")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            data.get("likes_count"),
            0
        )
        self.assertEqual(
            data.get("dislikes_count"),
            0
        )
        self.assertEqual(
            data.get("like"),
            False
        )
        self.assertEqual(
            data.get("dislike"),
            False
        )
        self.assertEqual(
            response.data.get("message"),
            "Dislike removed"
        )

    def test_liking_comment_more_than_once(self):
        """
        Tests liking of a comment more than once
        """
        response = self.like_a_comment_more_than_once()
        data = response.data.get("comment").get("likes_info")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            data.get("likes_count"),
            0
        )
        self.assertEqual(
            data.get("dislikes_count"),
            0
        )
        self.assertEqual(
            data.get("like"),
            False
        )
        self.assertEqual(
            data.get("dislike"),
            False
        )
        self.assertEqual(
            response.data.get("message"),
            "Comment unliked"
        )

    def test_liking_disliked_comment(self):
        """
        Tests liking of a disliked comment
        """
        response = self.like_disliked_comment()
        data = response.data.get("comment").get("likes_info")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            data.get("likes_count"),
            1
        )
        self.assertEqual(
            data.get("like"),
            True
        )
        self.assertEqual(
            data.get("dislikes_count"),
            0
        )
        self.assertEqual(
            data.get("dislike"),
            False
        )
        self.assertEqual(
            response.data.get("message"),
            "Comment liked"
        )

    def test_disliking_liked_comment(self):
        """
        Tests liking of disliked comment
        """
        response = self.dislike_liked_comment()
        data = response.data.get("comment").get("likes_info")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            data.get("likes_count"),
            0
        )
        self.assertEqual(
            data.get("like"),
            False
        )
        self.assertEqual(
            data.get("dislikes_count"),
            1
        )
        self.assertEqual(
            data.get("dislike"),
            True
        )
        self.assertEqual(
            response.data.get("message"),
            "Comment disliked"
        )
