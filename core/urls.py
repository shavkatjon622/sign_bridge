from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LessonCategoryViewSet, LessonViewSet, WordCategoryViewSet, WordViewSet

# Router yaratamiz, u barcha manzillarni o'zi avtomatlashtiradi
router = DefaultRouter()
router.register(r'lesson-categories', LessonCategoryViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'word-categories', WordCategoryViewSet)
router.register(r'words', WordViewSet)

# Endi hammasini routerga topshiramiz
urlpatterns = [
    path('', include(router.urls)),
]