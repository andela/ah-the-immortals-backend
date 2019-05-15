from django.shortcuts import get_object_or_404
from django.utils import timezone
from notifications.models import Notification
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import (GenericAPIView, ListAPIView,
                                     RetrieveUpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authors.apps.appnotifications.models import UserNotification
from authors.apps.authentication.models import User

from .serializers import NotificationSerializer, Subscription


class SubscribeUnsubscribeAPIView(RetrieveUpdateAPIView):
    """
    lets users to subscribe and unsubscribe to notifications.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = Subscription

    def update(self, request, *args, **kwargs):
        user = UserNotification.objects.get(user=request.user)
        serializer_data = request.data
        serializer = self.serializer_class(
            instance=user, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UnsubscribeEmailAPIView(GenericAPIView):
    """
    lets users to unsubscribe from email notifications.
    """
    serializer_class = Subscription

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        token_object = Token.objects.get(key=token)
        user = token_object.user
        user = UserNotification.objects.get(user=user)
        user.email_notifications = False
        user.save()
        resp = {
            "message": "You have unsubscribed from email notifications"
        }
        return Response(data=resp, status=status.HTTP_200_OK)


class NotificationApiView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        notifications = self.notifications(request)
        serializer = self.serializer_class(
            notifications, many=True
        )
        if notifications.count() == 0:
            resp = {
                "message": "You have no new notifications",
                "notifications": serializer.data
            }
        else:
            resp = {
                "message": f"You have {notifications.count()} notification(s)",
                "notifications": serializer.data
            }
        return Response(resp)


class AllNotificationsAPIview(NotificationApiView):
    """
    list all user's notifications
    """

    def notifications(self, request):
        request.user.notifications.mark_all_as_read()
        return request.user.notifications.active()

    def delete(self, request, *args, **kwargs):
        if request.user.notifications.active():
            request.user.notifications.mark_all_as_deleted()
            resp = {
                'message': 'Notifications deleted successfully'
            }
        else:
            resp = {
                'message': 'No notifications found'
            }
        return Response(resp)


class UnreadNotificationsAPIview(NotificationApiView):
    """
    list all user's unread notifications
    """

    def notifications(self, request):
        request.user.notifications.unread()
        return request.user.notifications.active()


class DeleteSingleNotificationAPIView(NotificationApiView):
    """
    delete a single notification
    """

    def delete(self, request, *args, **kwargs):
        try:
            notif = request.user.notifications.active().get(id=kwargs['id'])
            notif.deleted = True
            notif.save()
            resp = {
                'message': 'Notification deleted successfully'
            }
        except Exception:
            resp = {
                'message': 'No notification found with that id'
            }
        return Response(resp)
