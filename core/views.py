from rest_framework import generics
from .models import Lesson, Test, TestResult, LessonProgress
from .serializers import LessonSerializer, TestSerializer, TestSubmitSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone


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


class TestSubmitAPIView(APIView):

    def post(self, request):
        serializer = TestSubmitSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            user = request.user  # keyin JWT qo‘shamiz

            try:
                test = Test.objects.get(id=data["test_id"])
            except Test.DoesNotExist:
                return Response(
                    {"error": "Test not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            with transaction.atomic():

                # TestResult yaratish
                test_result, created = TestResult.objects.update_or_create(
                    user=user,
                    test=test,
                    defaults={
                        "score": data["score"],
                        "percentage": data["percentage"],
                        "xp_earned": data["xp_earned"],
                    },
                )

                # XP qo‘shish
                user.xp += data["xp_earned"]
                user.save()

                # Lesson complete qilish (agar xohlasang)
                LessonProgress.objects.update_or_create(
                    user=user,
                    lesson=test.lesson,
                    defaults={
                        "is_completed": True,
                        "completed_at": timezone.now(),
                    },
                )

            return Response(
                {
                    "message": "Test submitted successfully",
                    "total_xp": user.xp,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# test submit uchun quyidagi shablonda malumot qabul qilishi kerak.
    # {
    #     "test_id": 1,
    #     "score": 8,
    #     "percentage": 80,
    #     "xp_earned": 40
    # }