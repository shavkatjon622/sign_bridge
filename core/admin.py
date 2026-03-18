from django.contrib import admin
from .models import User, LessonCategory, Category, Word, Lesson, LessonProgress, Test, Question, QuestionOption, TestResult

# User uchun maxsus ko'rinish
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'xp')
    search_fields = ('username', 'email', 'phone')

@admin.register(LessonCategory)
class LessonCategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('text', 'text_uz', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('text', 'text_uz', 'text_ru')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'xp_reward', 'views_count')
    list_filter = ('category',)
    search_fields = ('title',)

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson')
    search_fields = ('title',)

# ==========================================
# SAVOLLAR VA JAVOBLAR (INLINE SYSTEM)
# ==========================================
class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 2 # Odatiy bo'sh turadigan variantlar soni (frontda ko'pincha 2 yoki 4 ta)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('get_question_name', 'test', 'question_type')
    list_filter = ('question_type',)
    search_fields = ('text', 'test__title')
    inlines = [QuestionOptionInline] # Savol yaratish oynasida variantlarni ham chiqarish

    def get_question_name(self, obj):
        return obj.text if obj.text else f"Rasm/Video savol: {obj.id}"
    get_question_name.short_description = 'Savol matni'

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'completed_at')
    list_filter = ('is_completed',)

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'percentage', 'xp_earned')
    list_filter = ('user',)