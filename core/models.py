from django.db import models
from django.contrib.auth.models import AbstractUser


# =========================
# Custom User
# =========================
class User(AbstractUser):
    # AbstractUser o'zida email, first_name (ism), last_name (familiya) ni saqlaydi.
    # Ularni qayta yozish shart emas.
    phone = models.CharField(max_length=50, unique=True, null=True, blank=True)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    xp = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)  # Avatar qo'shildi

    def __str__(self):
        return self.username or self.email


# =========================
# Lesson & Categories
# =========================
class LessonCategory(models.Model):  # Yangi: Darslar uchun kategoriya
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='lesson_categories/')

    def __str__(self):
        return self.title


class Lesson(models.Model):
    category = models.ForeignKey(LessonCategory, on_delete=models.CASCADE, related_name="lessons",
                                 null=True)  # Kategoriyaga ulandi
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField()
    xp_reward = models.IntegerField(default=10)
    views_count = models.IntegerField(default=0)  # Yangi: Prosmotrlar soni
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# Words & Categories
# =========================
class Category(models.Model):  # So'zlar uchun kategoriya
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='word_categories/', null=True, blank=True)  # Yangi: Rasm qo'shildi

    def __str__(self):
        return self.name


class Word(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="words")
    text = models.CharField(max_length=100)
    text_uz = models.CharField(max_length=100, blank=True, null=True)
    text_ru = models.CharField(max_length=100, blank=True, null=True)
    definition = models.TextField(blank=True, null=True)
    video_url = models.FileField(upload_to='words/videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


# =========================
# Progress & Tracking
# =========================
class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progresses')  # related_name qo'shildi
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "lesson")

    def __str__(self):
        return f"{self.user} - {self.lesson.title}"


# =========================
# Test & Questions System (Yangi arxitektura)
# =========================
class Test(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='tests')
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        (1, "Matnli savol (2 ta video javob)"),
        (2, "Rasmli savol (2 ta rasm javob)"),
        (3, "Videoli savol (4 ta matn javob)"),
    ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    question_type = models.IntegerField(choices=QUESTION_TYPES, default=1)

    # Savolning o'zi ham matn, rasm yoki video bo'lishi mumkin
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='questions/images/', blank=True, null=True)
    video_url = models.FileField(upload_to='questions/videos/', blank=True, null=True)


    def __str__(self):
        return f"{self.get_question_type_display()} - {self.test.title}"


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')

    # Javob variantlari ham matn, rasm yoki video bo'lishi mumkin
    text = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='options/images/', blank=True, null=True)
    video_url = models.FileField(upload_to='options/videos/', blank=True, null=True)
    is_correct = models.BooleanField(default=False)  # Qaysi biri to'g'riligini belgilash uchun

    def __str__(self):
        return f"Option for {self.question.id} - Correct: {self.is_correct}"


class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.IntegerField()
    percentage = models.FloatField()
    xp_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "test")

    def __str__(self):
        return f"{self.user} - {self.test.title} - {self.score}"