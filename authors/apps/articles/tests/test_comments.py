import json
from rest_framework import status

from authors.apps.articles.models import Comment

from .basetests import BaseTest


class TestComments(BaseTest):
    """
    Class to test comments
    """
    error = "Article does not exist"
    msg = "Comment or the Article was not found"
    body = "unsuccesful update either the comment orslug not found"
    msgg = 'unsuccesful update either the comment orslug not found'
    message = 'Comment deleted successfully'
    no_update = 'unsuccesful update either the comment orslug not found'
    no_comment = 'no comments on this article'
    no_comment_with_id = 'This article does not have a comment with that id'

    def test_successful_comment_creation(self):
        """
        Test successful creation of a comment
        """
        response = self.create_comment()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_successful_comment_creation_by_id(self):
        """
        Test successful creation of a reply comment
        """
        response = self.create_child_comment()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unsuccessful_comment_creation_by_id(self):
        """
        Test unsuccessful creation of a reply comment
        """
        response = self.create_child_comment_not_found()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {'errors': {
                         'parent': ['Invalid pk "1" - object does not exist.']}})

    def test_unsuccessful_comment_creation(self):
        """
        Test unsuccessful creation of a comment
        """
        response = self.create_comment_fail()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], self.error)

    def test_successful_get_all_comments(self):
        """
        Test get all comments
        """
        response = self.get_all_comments()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unsuccessful_delete_comment(self):
        """
        Test unsuccessful delete comment
        """
        response = self.delete_comment()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], self.msg)

    def test_successful_delete_comment(self):
        """
        Test successful delete comment
        """
        response = self.delete_comment_succefully()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), {'message': {
                         'body': [self.message]}})

    def test_update_comment_unsecceful(self):
        """
        Test update comment unsecceful
        """
        response = self.update_comment_unsuccefully()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {
                         'error': {'body': [self.no_update]}})

    def test_update_comment_successful(self):
        """
        Test update comment successful
        """
        response = self.update_comment_succefully()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment_successful_history_twice(self):
        """
        Test update comment successful
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.update_comment_exist_in_history("I love myself")
        response = self.update_comment_exist_in_history("I love myself")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"),
                         "No changes detected on the comment")

    def test_update_comment_not_own_history(self):
        """
        Test update comment successful
        """
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        response = self.update_comment_exist_in_history("I love myself")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("detail"),
                         "You cannot edit or delete a comment you dont own")

    def test_delete_comment_not_own_history(self):
        """
        Test update comment successful
        """
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        response = self.delete_comment_for_history()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("detail"),
                         "You cannot edit or delete a comment you dont own")

    def test_successful_get_one_comment(self):
        """
        Test one comment
        """
        response = self.get_all_comments()
        comment = Comment.objects.all()[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get(
            'comments')[0].get('body'), comment.body)

    def test_get_one_comment_not_found(self):
        """
        Test one comment not found
        """
        response = self.get_one_comment_not_found()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {
                         'comments': self.no_comment})

    def test_unsuccessful_get_one_comment_by_id(self):
        """
        Test unsuccessful get one comment
        """
        response = self.get_comments_by_id()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {
                         'comments': self.no_comment_with_id})

    def test_get_one_comment(self):
        """
        Test one comment
        """
        response = self.get_comment_by_id()
        comment = Comment.objects.all()[0]
        comment_id = comment.id
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment']['body'], comment.body)
        self.assertEqual(response.data['comment']['parent'], None)

    def test_get_history_comment(self):
        """
        Test update comment with post history comment
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.update_comment_exist_in_history("I love this program")
        response = self.get_one_comment_history()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("comment_history").get("body"),
                         "This is a test history comment")

    def test_get_history_comment_all(self):
        """
        Test update comment with post history comment
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.update_comment_exist_in_history("I love this program Some more")
        response = self.get_all_comment_history()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("comments_history")[0].get("body"),
                         "This is a test history comment")

    def test_get_history_comment_no_history(self):
        """
        Test update comment with post history comment
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.get_one_comment_history_not_found()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error"),
                         "History comment selected does not exist")

    def test_get_history_comment_all_no_history(self):
        """
        Test update comment with post history comment
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.get_all_comment_history_not_found()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"),
                         "No history comments")
