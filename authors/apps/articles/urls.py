from django.urls import path
from .views import (
    ListCreateArticleAPIView,
    RetrieveUpdateArticleAPIView,
    FetchTags
)

app_name = 'articles'

urlpatterns = [
    path('articles/', ListCreateArticleAPIView.as_view(), name='article'),
    path('articles/<slug>/', RetrieveUpdateArticleAPIView.as_view(),
         name='articles'),
    path('tags/', FetchTags.as_view(), name="all_tags")
]
