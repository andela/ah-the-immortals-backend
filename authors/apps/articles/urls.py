from django.urls import path
from .views import (
    ListCreateArticleAPIView,
    RetrieveUpdateArticleAPIView,
    FetchTags,
    LikeDislikeView,
    FavoritesView,
    ListUserFavoriteArticlesView)

app_name = 'articles'

urlpatterns = [
    path('articles/', ListCreateArticleAPIView.as_view(), name='article'),
    path('articles/<slug>/', RetrieveUpdateArticleAPIView.as_view(),
         name='articles'),
    path('tags/', FetchTags.as_view(), name="all_tags"),
    path('articles/<str:slug>/<str:vote_type>/vote/',
         LikeDislikeView.as_view(), name='likes'),
    path('articles/<str:slug>/favorite/',
         FavoritesView.as_view(), name='favorite'),
    path('articles/favorites/me/',
         ListUserFavoriteArticlesView.as_view(), name='get_favorite'),
]
