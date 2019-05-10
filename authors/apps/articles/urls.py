from django.conf.urls import url
from django.urls import path

from .views import (CommentAPIView, CommentDetailAPIView, FavoritesView,
                    FetchTags, LikeDislikeView, ListCreateArticleAPIView,
                    ListUserFavoriteArticlesView, RateArticleAPIView,
                    RetrieveUpdateArticleAPIView)

app_name = 'articles'

urlpatterns = [
    path('articles/', ListCreateArticleAPIView.as_view(), name='article'),
    path('articles/<slug>', RetrieveUpdateArticleAPIView.as_view(),
         name='articles'),
    path('tags/', FetchTags.as_view(), name="all_tags"),
    path('articles/<str:slug>/<str:vote_type>/vote/',
         LikeDislikeView.as_view(), name='likes'),
    path('articles/<str:slug>/favorite/',
         FavoritesView.as_view(), name='favorite'),
    path('articles/favorites/me/',
         ListUserFavoriteArticlesView.as_view(), name='get_favorite'),
    path('articles/<slug>/rate/',
         RateArticleAPIView.as_view(), name='rating_articles'),
    path('articles/<slug>/comments/',
         CommentAPIView.as_view(), name='comment'),
    path('articles/<slug>/comments/<id>/',
         CommentDetailAPIView.as_view(), name='commentdetail')
]
