from rest_framework.decorators import action
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import User
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import LessonCategory, Lesson, Category, Word, Test, LessonProgress, QuestionOption, TestResult
from .serializers import LessonCategorySerializer, LessonSerializer, CategorySerializer, WordSerializer, TestListSerializer, TestDetailSerializer, GoogleLoginSerializer, LogoutSerializer, UserProfileSerializer, UserUpdateSerializer

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
    filter_backends = [filters.SearchFilter]
    search_fields = ['text', 'text_uz', 'text_ru', 'definition']


class TestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Test.objects.all()

    # Qaysi Serializer ishlatishni dinamik hal qilamiz
    def get_serializer_class(self):
        if self.action == 'list':
            return TestListSerializer  # Ro'yxat uchun qisqa ma'lumot
        return TestDetailSerializer  # Bitta testni ID bilan ochganda to'liq ma'lumot


class GoogleLoginView(GenericAPIView):
    serializer_class = GoogleLoginSerializer  # Swagger shu qolipga qarab chizadi
    permission_classes = []  # Hamma uchun ochiq

    def post(self, request, *args, **kwargs):
        # Ma'lumot to'g'ri kelganini tekshiramiz
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']  # Tekshirilgan tokenni olamiz

        try:
            # Google tokenni tekshiramiz
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())

            email = idinfo.get('email')
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            google_id = idinfo.get('sub')

            user, created = User.objects.get_or_create(email=email, defaults={
                'username': email.split('@')[0],
                'first_name': first_name,
                'last_name': last_name,
                'google_id': google_id
            })

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'is_new_user': created,
                'user_info': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': f"{user.first_name} {user.last_name}".strip()
                }
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Yaroqsiz yoki eskirgan Google token"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()  # Tokenni kuydiramiz
            return Response({"message": "Tizimdan muvaffaqiyatli chiqildi"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Xatolik yuz berdi yoxud token allaqachon eskirgan"}, status=status.HTTP_400_BAD_REQUEST)


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all().order_by('-created_at')
    serializer_class = LessonSerializer

    # Yangi: Dars ko'rilganini belgilash API'si
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def view_lesson(self, request, pk=None):
        lesson = self.get_object()  # ID bo'yicha darsni topamiz
        user = request.user

        # Prosmotrni bittaga oshiramiz
        lesson.views_count += 1
        lesson.save()

        # User uchun Progress ochamiz (agar oldin ochilmagan bo'lsa)
        progress, created = LessonProgress.objects.get_or_create(user=user, lesson=lesson)

        # Agar darsni to'liq ko'rdim deb signal kelsa, completed qilib qo'yamiz
        if request.data.get('is_completed') == True and not progress.is_completed:
            progress.is_completed = True
            from django.utils import timezone
            progress.completed_at = timezone.now()
            progress.save()

        return Response({"message": "Dars ko'rildi", "views_count": lesson.views_count})


class TestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Test.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TestListSerializer
        return TestDetailSerializer

    # Yangi: Test javoblarini tekshirish va XP berish API'si
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_test(self, request, pk=None):
        test = self.get_object()
        user = request.user

        # Ilovadan keladigan javoblar ro'yxati (Masalan: [{"question_id": 1, "option_id": 4}, ...])
        user_answers = request.data.get('answers', [])

        if not user_answers:
            return Response({"error": "Javoblar yuborilmadi"}, status=status.HTTP_400_BAD_REQUEST)

        total_questions = test.questions.count()
        correct_answers_count = 0

        # Javoblarni bittalab tekshiramiz
        for answer in user_answers:
            question_id = answer.get('question_id')
            option_id = answer.get('option_id')

            # Agar tanlangan variant haqiqatan ham shu savolga tegishli va to'g'ri bo'lsa
            is_correct = QuestionOption.objects.filter(
                id=option_id,
                question_id=question_id,
                is_correct=True
            ).exists()

            if is_correct:
                correct_answers_count += 1

        # Natijani hisoblaymiz
        percentage = (correct_answers_count / total_questions) * 100 if total_questions > 0 else 0

        # XP hisoblaymiz (Masalan: Dars uchun 100 XP belgilangan bo'lsa va 80% topsa, 80 XP oladi)
        xp_earned = int((percentage / 100) * test.lesson.xp_reward)

        # Natijani bazaga saqlaymiz (Yoki oldin ishlagan bo'lsa yangilaymiz)
        result, created = TestResult.objects.update_or_create(
            user=user,
            test=test,
            defaults={
                'score': correct_answers_count,
                'percentage': percentage,
                'xp_earned': xp_earned
            }
        )

        # Userning umumiy XP siga faqat yangi ishlab topilgan XP ni qo'shamiz (bu logikani ehtiyojga qarab o'zgartirish mumkin)
        # Hozircha eng yuqori natijasini hisoblaymiz. Agar qayta ishlab ko'proq topsa, farqini qo'shamiz:
        if not created and result.xp_earned < xp_earned:
            xp_diff = xp_earned - result.xp_earned
            user.xp += xp_diff
            user.save()
        elif created:
            user.xp += xp_earned
            user.save()

        return Response({
            "message": "Test yakunlandi",
            "total_questions": total_questions,
            "correct_answers": correct_answers_count,
            "percentage": percentage,
            "xp_earned": xp_earned,
            "total_user_xp": user.xp
        }, status=status.HTTP_200_OK)

class UserProfileView(GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated] # Faqat login qilganlar ko'ra oladi

    def get(self, request, *args, **kwargs):
        # Murojaat qilayotgan odamni (request.user) olib, uning ma'lumotlarini qolipga solamiz
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Rasm (fayl) qabul qila olishi uchun kerak

    # Qaysi so'rov kelishiga qarab Swagger'ga mos qolipni beramiz
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer

    # GET: Profilni ko'rish (Eski mantiq)
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PATCH: Profilni qisman yangilash (Faqat ism yoki faqat rasm jo'natsa ham ishlaydi)
    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Yangilangandan keyin, to'liq ma'lumotni (XP va darslar bilan qo'shib) qaytaramiz
        return_serializer = UserProfileSerializer(request.user)
        return Response(return_serializer.data, status=status.HTTP_200_OK)