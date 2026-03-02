from django.urls import path
from .views import (
    LessonListAPIView,
    LessonDetailAPIView,
    TestDetailAPIView,
    TestSubmitAPIView,
    GoogleAuthAPIView,
)

urlpatterns = [
    path("lessons/", LessonListAPIView.as_view()),
    path("lessons/<int:pk>/", LessonDetailAPIView.as_view()),
    path("tests/<int:pk>/", TestDetailAPIView.as_view()),
    path("tests/submit/", TestSubmitAPIView.as_view()),
    path("auth/google/", GoogleAuthAPIView.as_view()),
]