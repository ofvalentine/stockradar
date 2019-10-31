from django.urls import path
from .views import KeywordsView, TopicsView

urlpatterns = [
    path('keywords/', KeywordsView.as_view()),
    path('topics/', TopicsView.as_view()),
]