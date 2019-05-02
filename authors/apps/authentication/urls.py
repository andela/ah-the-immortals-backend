from django.conf.urls import url
from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,
    SocialAuthAPIView
)

app_name = 'authentication'

urlpatterns = [
    url(r'^user/?$', UserRetrieveUpdateAPIView.as_view(), name='update_get'),
    url(r'^users/?$', RegistrationAPIView.as_view(), name='registration'),
    url(r'^users/login/?$', LoginAPIView.as_view(), name='login'),
    path('oauth/', SocialAuthAPIView.as_view(), name='social'),
]
