from django.conf.urls import url
from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,
    SignupEmailVerificationView,
    SocialAuthAPIView,
    PasswordResetView,
    PasswordResetConfirmView
)

app_name = 'authentication'

urlpatterns = [
    url(r'^user/?$', UserRetrieveUpdateAPIView.as_view(), name='update_get'),
    url(r'^users/?$', RegistrationAPIView.as_view(), name='registration'),
    url(r'^users/login/?$', LoginAPIView.as_view(), name='login'),
    path('users/oauth/', SocialAuthAPIView.as_view(), name='social'),
    path('users/password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('users/password/reset/confirm/',
         PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('users/activate/<str:token>',
         SignupEmailVerificationView.as_view(), name='signup_verification'),
    path('users/oauth/', SocialAuthAPIView.as_view(), name='social'),
    path('users/password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('users/password/reset/confirm/',
         PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
