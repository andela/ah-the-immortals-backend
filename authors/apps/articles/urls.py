from django.urls import path
from .views import ListCreateArticleAPIView, RetrieveUpdateArticleAPIView

app_name = 'articles'

urlpatterns = [
    path('articles/', ListCreateArticleAPIView.as_view(), name='article'),
    path('articles/<slug>/', RetrieveUpdateArticleAPIView.as_view(),
         name='articles'),
]
