from rest_framework import serializers
from .models import LessonCategory, Lesson, Category, Word, QuestionOption, Question, Test, User, LessonProgress

# Dars kategoriyalari uchun
class LessonCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonCategory
        fields = ['id', 'title', 'image']

# Darslar uchun
class LessonSerializer(serializers.ModelSerializer):
    category = LessonCategorySerializer(read_only=True) # Kategoriyani to'liq ma'lumoti bilan qaytaradi

    class Meta:
        model = Lesson
        fields = ['id', 'category', 'title', 'description', 'video_url', 'xp_reward', 'views_count', 'created_at']

# So'z kategoriyalari uchun
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']

# So'zlar uchun
class WordSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Word
        fields = ['id', 'category', 'text', 'text_uz', 'text_ru', 'definition', 'video_url', 'created_at']




class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'text', 'image', 'video_url', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    # 'options' degan nom models.py da related_name='options' deb berilgani uchun ishlaydi
    options = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_type', 'text', 'image', 'video_url', 'options']

class TestDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ['id', 'title', 'lesson', 'questions']


class TestListSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField() # Savollar sonini sanash uchun

    class Meta:
        model = Test
        fields = ['id', 'title', 'lesson', 'questions_count']

    def get_questions_count(self, obj):
        return obj.questions.count() # Shu testga tegishli savollar sonini sanab beradi


class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField(
        required=True,
        help_text="Google tomonidan berilgan uzun id_token"
    )

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        required=True,
        help_text="Foydalanuvchining ayni paytdagi refresh tokeni"
    )


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    completed_lessons_count = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'avatar', 'xp', 'completed_lessons_count', 'completed_lessons']

    # Ism va familiyani qoshib bitta qilib beradi
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

    # Tugatilgan darslar sonini hisoblaydi
    def get_completed_lessons_count(self, obj):
        return LessonProgress.objects.filter(user=obj, is_completed=True).count()

    # Tugatilgan darslarning qisqacha ro'yxatini beradi (Mobile ilovada ro'yxat qilib chiqarish uchun)
    def get_completed_lessons(self, obj):
        progresses = LessonProgress.objects.filter(user=obj, is_completed=True)
        return [{"id": p.lesson.id, "title": p.lesson.title, "completed_at": p.completed_at} for p in progresses]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'avatar']