from django.urls import path

from authors.apps.profiles.views import (UserProfileView, UpdateUserProfileView)

app_name = 'profiles'

urlpatterns = [
    path('profiles/<str:username>', UserProfileView.as_view(), name='profile'),
    path('profiles/<str:username>/', UpdateUserProfileView.as_view(), name='update_profile'),
]
