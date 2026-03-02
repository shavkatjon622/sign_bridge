from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework import generics
from .models import Lesson, Test, TestResult, LessonProgress, User
from .serializers import LessonSerializer, TestSerializer, TestSubmitSerializer, GoogleAuthSerializer
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

# 🎥 Lesson List
class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# 🎥 Lesson Detail
class LessonDetailAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


#  Test Detail (savollari bilan)
class TestDetailAPIView(generics.RetrieveAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class TestSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

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




class GoogleAuthAPIView(APIView):

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        token = serializer.validated_data["id_token"]

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError:
            return Response({"error": "Invalid token"}, status=400)

        email = idinfo.get("email")
        google_id = idinfo.get("sub")
        full_name = idinfo.get("name")

        if not email:
            return Response({"error": "Email not provided"}, status=400)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "google_id": google_id,
                "first_name": full_name or "",
            },
        )

        # Agar oldin oddiy user bo‘lsa, google_id update qilamiz
        if not user.google_id:
            user.google_id = google_id
            user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "xp": user.xp,
                },
            }
        )