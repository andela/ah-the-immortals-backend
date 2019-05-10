from rest_framework import serializers
from notifications.models import Notification
from authors.apps.articles.models import Article
from authors.apps.authentication.models import User
from .models import UserNotification


class Subscription(serializers.ModelSerializer):
    """
    serializer class for unsubscribing from either email or in-app
    notifications
    """
    class Meta:
        model = UserNotification
        fields = ('email_notifications_subscription',
                  'in_app_notifications_subscription')


class NotificationSerializer(serializers.ModelSerializer):
    """
    serializer class for notification objects
    """
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Notification
        fields = (
            'id',
            'unread',
            'verb',
            'timestamp',
            'description'
            )
