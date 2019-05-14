import json

from rest_framework.views import status
from .basetest import BaseTest


class EscalationArticlesTest(BaseTest):
    """
    Test cases for article escalation
    """
    msg = "Sorry we couldn't find that article."
    snitch = "You can't report your article."
    user_delete = "Only Admins can delete a reported article"
    report_twice = "You are not allowed to report twice"
    admin_delete = "You successfully deleted the article"
    get_admin = "Only Admins can get reported article"

    def test_escalation_of_a_404_article(self):
        """
        Test successful escalation of an article that doesn't exist
        """
        token = self.user1.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.escalate_an_article()
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.data["detail"], self.msg)

    def test_escalation_of_an_article(self):
        """
        Test successful article escalation
        """
        token = self.user1.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.escalate_an_article_successfully()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_update_escalation_of_an_article(self):
        """
        Test successful updating an  escalation
        """
        token = self.user1.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.update_an_escalated_article()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_escalation_of_an_article_with_author(self):
        """
        Test escalation with author
        """
        token = self.user2.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.escalate_an_article_successfully()
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_escalation_of_an_article_twice(self):
        """
        Test unsuccessful article escalation twice
        """
        token = self.user1.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.escalate_an_article_twice()
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"], self.report_twice)

    def test_delete_of_an_escalated_article_with_user(self):
        """
        Test unsuccessful article escalation deletion
        """
        token = self.user1.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.delete_article()
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(resp.data["error"], self.user_delete)

    def test_delete_of_an_escalated_article_with_admin(self):
        """
        Test successful article escalation deletion
        """
        token = self.user3.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.delete_article()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["message"], self.admin_delete)

    def test_getting_of_an_escalated_article_with_admin(self):
        """
        Test successful getting escalated articles
        """
        token = self.user3.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        self.escalate_an_article_successfully()
        resp = self.get_article()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get("escalated articles")[0].get('article').get('title'), 'this is mine')

    def test_getting_of_an_escalated_article_with_users(self):
        """
        Test unsuccessful getting escalated articles
        """
        token = self.user1.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.get_article()
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(resp.data["error"], self.get_admin)
