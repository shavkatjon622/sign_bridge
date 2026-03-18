from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LessonCategoryViewSet, LessonViewSet, WordCategoryViewSet,
    WordViewSet, TestViewSet, GoogleLoginView, LogoutView, UserProfileView # Importlarni qo'shdik
)

# Router yaratamiz, u barcha manzillarni o'zi avtomatlashtiradi
router = DefaultRouter()
router.register(r'lesson-categories', LessonCategoryViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'word-categories', WordCategoryViewSet)
router.register(r'words', WordViewSet)
router.register(r'tests', TestViewSet)

# Endi hammasini routerga topshiramiz
urlpatterns = [
    path('', include(router.urls)),
    # Login va Logout uchun alohida manzillar:
    path('auth/google-login/', GoogleLoginView.as_view(), name='google_login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
]