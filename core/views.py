from rest_framework import viewsets
from .models import LessonCategory, Lesson, Category, Word
from .serializers import LessonCategorySerializer, LessonSerializer, CategorySerializer, WordSerializer

class LessonCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LessonCategory.objects.all()
    serializer_class = LessonCategorySerializer

class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all().order_by('-created_at') # Eng yangilari birinchi chiqadi
    serializer_class = LessonSerializer

class WordCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class WordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Word.objects.all().order_by('-created_at')
    serializer_class = WordSerializer