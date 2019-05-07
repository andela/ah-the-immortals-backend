from ...articles.tests.basetests import BaseTest
from rest_framework.reverse import reverse


class NotificationBaseTest(BaseTest):
    """
    Base test case for testing notifications
    """

    follow_url = reverse("profiles:follow", args=["adam"])
    notification_url = reverse("notifications:all-notifications")
    unread_notification_url = reverse("notifications:unread-notifications")
    subscribe_unsubscribe_url = reverse("notifications:subscription")

    def follow_user(self):
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        self.client.post(self.follow_url)
