from django.db import models
from django.contrib.auth.models import AbstractUser


# =========================
# Custom User
# =========================

class User(AbstractUser):
    phone = models.CharField(max_length=50, unique=True, null=True, blank=True)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    xp = models.IntegerField(default=0)

    def __str__(self):
        return self.username


# =========================
# Category
# =========================

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# =========================
# Word
# =========================

class Word(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="words")
    text = models.CharField(max_length=100)
    text_uz = models.CharField(max_length=100, blank=True, null=True)
    text_ru = models.CharField(max_length=100, blank=True, null=True)
    definition = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


# =========================
# Lesson
# =========================

class Lesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField()
    xp_reward = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# Lesson Progress
# =========================

class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "lesson")

    def __str__(self):
        return f"{self.user} - {self.lesson}"


# =========================
# Test
# =========================

class Test(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


# =========================
# Question
# =========================

class Question(models.Model):
    OPTION_CHOICES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question_text = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)

    def __str__(self):
        return self.question_text[:50]


# =========================
# Test Result
# =========================

class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.test} - {self.score}"