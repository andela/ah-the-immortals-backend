from rest_framework import status
from .basetest import NotificationBaseTest
from rest_framework.reverse import reverse


class TestNotifications(NotificationBaseTest):
    """
    Class to test notifications
    """

    def test_successful_notification_article(self):
        """
        Test for successful notification of a user upon article creation
        """
        self.follow_user()
        self.create_article()
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        response = self.client.get(self.notification_url)
        self.assertEqual(
            response.data['message'], 'You have 1 notification(s)')
        self.assertIn('notifications', str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_notifications(self):
        """
        Test user having no notifications
        """
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        response = self.client.get(self.notification_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_unread_notifications(self):
        """
        Test retrieval of unread notifications
        """
        self.follow_user()
        self.create_article()
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        response = self.client.get(self.unread_notification_url)
        self.assertIn('notifications', str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subscribe_notififications(self):
        """
        Test subscribing and unsubscribing of notifications
        """
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        response = self.client.patch(self.subscribe_unsubscribe_url, {
            'email_notifications_subscription': 'false',
            'in_app_notifications_subscription': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unsubscribe_email_notification(self):
        """
        Test unsubscribing from email notifications
        """
        response = self.client.get(reverse("notifications:opt_out_link",
                                           args=[self.get_token()]))
        self.assertEqual(response.data['message'],
                         'You have unsubscribed from email notifications')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_from_comments(self):
        """
        Test notifications from comments
        """
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        self.post_favorite()
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.post_comment()
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        response = self.client.get(self.notification_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_notifications_while_unsubscribed(self):
        """
        Test getting notifications while user has unsubscribed
        """
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        self.client.patch(self.subscribe_unsubscribe_url, {
            'email_notifications_subscription': 'false',
            'in_app_notifications_subscription': 'false'})
        response = self.client.get(self.notification_url)
        self.assertEqual(response.data['message'],
                         'You are not subscribed to in app notifications')

    def test_delete_notifications(self):
        """
        Tests successful deletion of notifications
        """
        self.follow_user()
        self.create_article()
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        response = self.client.delete(self.notification_url)
        self.assertEqual(response.data['message'],
                         'Notifications deleted successfully')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_unfound_notifications(self):
        """
        Tests deletion of unfound notifications
        """
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        response = self.client.delete(self.notification_url)
        self.assertEqual(response.data['message'], 'No notifications found')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
