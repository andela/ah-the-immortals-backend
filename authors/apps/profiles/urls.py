from django.urls import path
from django.urls import include, path
from django.conf.urls import url
from .views import FollowAPI, FollowersAPI

from authors.apps.profiles.views import (
    UserProfileView, UpdateUserProfileView, UserListView)

from authors.apps.profiles.views import (
    UserProfileView, UpdateUserProfileView)

app_name = 'profiles'

urlpatterns = [
    path('profiles/<str:username>', UserProfileView.as_view(), name='profile'),
    path('profiles/<str:username>/',
         UpdateUserProfileView.as_view(), name='update_profile'),
    path('profiles/<username>/followers/', FollowersAPI.as_view()),
    path('profiles/<username>/follow/', FollowAPI.as_view()),
    path('profiles/<str:username>/',
         UpdateUserProfileView.as_view(), name='update_profile'),
    path('profiles/', UserListView.as_view(), name='list_users'),
]
