from django.urls import path
from django.urls import include, path
from django.conf.urls import url
from authors.apps.profiles.views import (
    UserProfileView, UpdateUserProfileView,
    UserListView, MyFollowersAPI, FollowAPI)

app_name = 'profiles'

urlpatterns = [
    path('profiles/<str:username>', UserProfileView.as_view(), name='profile'),
    path('profiles/<str:username>/',
         UpdateUserProfileView.as_view(), name='update_profile'),
    path('profiles/<username>/followers/', MyFollowersAPI.as_view()),
    path('profiles/<username>/follow/', FollowAPI.as_view(), name='follow'),
    path('profiles/<str:username>/',
         UpdateUserProfileView.as_view(), name='update_profile'),
    path('profiles/', UserListView.as_view(), name='list_users'),
]
