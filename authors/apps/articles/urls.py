from django.urls import path
from .views import (ListCreateArticleAPIView, RetrieveUpdateArticleAPIView,
                    CommentAPIView, CommentDetailAPIView)

app_name = 'articles'

urlpatterns = [
    path('articles/', ListCreateArticleAPIView.as_view(), name='article'),
    path('articles/<slug>/comments/',
         CommentAPIView.as_view(), name='comment'),
    path('articles/<slug>/comments/<id>/',
         CommentDetailAPIView.as_view(), name='commentdetail'),
    path('articles/<slug>/', RetrieveUpdateArticleAPIView.as_view(),
         name='articles'),
]
