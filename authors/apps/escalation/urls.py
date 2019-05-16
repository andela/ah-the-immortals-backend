from django.conf.urls import url
from django.urls import path

from .views import ExcalationAPIView, FetchExcalationAPIView


app_name = 'escalation'

urlpatterns = [
    path('article/<str:slug>/escalate/',
         ExcalationAPIView.as_view(), name='escalate'),
    path('article/escalate/',
         FetchExcalationAPIView.as_view(), name='get_escalate'),
]
