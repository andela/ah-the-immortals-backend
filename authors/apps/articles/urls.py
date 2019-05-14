from django.conf.urls import url
from django.urls import path, re_path

from .views import (CommentAPIView, CommentDetailAPIView, FavoritesView,
                    FetchTags, LikeDislikeView, ListCreateArticleAPIView,
                    ListUserFavoriteArticlesView, RateArticleAPIView,
                    RetrieveUpdateArticleAPIView)

# from .filters import FilterArticlesView

app_name = 'articles'

urlpatterns = [
    path('articles/', ListCreateArticleAPIView.as_view(), name='article'),
    path('tags/', FetchTags.as_view(), name="all_tags"),
    path('articles/<slug>/comments/',
         CommentAPIView.as_view(), name='comment'),
    path('articles/<slug>/comments/<id>/',
         CommentDetailAPIView.as_view(), name='commentdetail'),
    path('articles/<slug>/', RetrieveUpdateArticleAPIView.as_view(),
         name='articles'),
    url(r'^articles/(?P<slug>[\w-]+)/(?P<vote_type>like|dislike)/$',
        LikeDislikeView.as_view(), name='likes'),
    path('articles/<str:slug>/favorite/',
         FavoritesView.as_view(), name='favorite'),
    path('articles/favorites/me/',
         ListUserFavoriteArticlesView.as_view(), name='get_favorite'),
    path('articles/<slug>/rate/',
         RateArticleAPIView.as_view(), name='rating_articles'),
]
