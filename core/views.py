from rest_framework import generics
from .models import Lesson, Test
from .serializers import LessonSerializer, TestSerializer


# 🎥 Lesson List
class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# 🎥 Lesson Detail
class LessonDetailAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# 📝 Test Detail (savollari bilan)
class TestDetailAPIView(generics.RetrieveAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer