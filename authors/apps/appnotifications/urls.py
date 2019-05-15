from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path(
        'notifications/',
        views.AllNotificationsAPIview.as_view(),
        name="all-notifications"
    ),
    path(
        'notifications/unread/',
        views.UnreadNotificationsAPIview.as_view(),
        name="unread-notifications"
    ),
    path(
        'notifications/subscription/',
        views.SubscribeUnsubscribeAPIView.as_view(),
        name="subscription"
    ),
    path(
        'notifications/unsubscribe_email/<str:token>/',
        views.UnsubscribeEmailAPIView.as_view(),
        name="opt_out_link"
    ),
    path(
        'notifications/<id>/',
        views.DeleteSingleNotificationAPIView.as_view(),
        name="deleteone"
    )
]
