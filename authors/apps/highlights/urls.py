from django.urls import path
from django.conf.urls import url

from authors.apps.highlights.views import (HighlightAPIView,
                                           RetrieveUpdateHighlightAPIView)

app_name = 'highlights'

urlpatterns = [
    path('articles/<slug>/highlight/', HighlightAPIView.as_view(),
         name='highlight'),
    path('articles/<slug>/highlight/<highlight_id>/',
         RetrieveUpdateHighlightAPIView.as_view(), name='highlights'),
]
