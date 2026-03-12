from rest_framework import serializers
from .models import LessonCategory, Lesson, Category, Word

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