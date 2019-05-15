from django.conf.urls import url
from django.urls import path, re_path

from .views import (
    CommentAPIView, CommentDetailAPIView, FavoritesView,
    FetchTags, LikeDislikeView, ListCreateArticleAPIView,
    ListUserFavoriteArticlesView, RateArticleAPIView,
    RetrieveUpdateArticleAPIView, SocialShareArticleView,
    CommentOneHistoryView,
    CommentAllHistoryView,
    GetBookMarksAPIVIew,
    DeleteBookMakeAPIView,
    BookmarkAPIView, SocialShareArticleView
)


app_name = 'articles'

urlpatterns = [
    path('articles/', ListCreateArticleAPIView.as_view(), name='article'),
    path('tags/', FetchTags.as_view(), name="all_tags"),
    path('articles/<slug>/comments/',
         CommentAPIView.as_view(), name='comment'),
    path('articles/<slug>/comments/<int:id>/',
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
    path("articles/<slug>/share/<provider>/",
         SocialShareArticleView.as_view(), name="share"),
    path('articles/<slug>/comments/<int:comment>/history/<int:id>/',
         CommentOneHistoryView.as_view(), name='history_'),
    path('articles/<slug>/comments/<int:comment>/history/',
         CommentAllHistoryView.as_view(), name='history_comments'),
    path('articles/<slug>/bookmark/', BookmarkAPIView.as_view(),
         name='bookmark'),
    path('articles/bookmark/<id>/', DeleteBookMakeAPIView.as_view(),
         name='book_mark'),
    path('article/bookmarks/', GetBookMarksAPIVIew.as_view(),
         name='bookmarks'),
]
