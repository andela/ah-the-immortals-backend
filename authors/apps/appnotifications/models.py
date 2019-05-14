from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from authors.apps.authentication.models import User

from ...utils import notification_handlers


class UserNotification(models.Model):
    """
    User Notification model stores user's preferences for notifications.
    By default all users are "opted in" to notifications
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True,
                                related_name='notification_preferences')
    email_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)


@receiver(post_save, sender=User)
def setup_notification_permissions(sender, **kwargs):
    instance = kwargs.get('instance')
    created = kwargs.get('created', False)

    if created:
        data = {
            'user': instance,
            'email_notifications': True,
            'in_app_notifications': True
        }
        UserNotification.objects.create(**data)
