from django.contrib import admin
from .models import User, Category, Word, Lesson, LessonProgress, Test, Question, TestResult

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Word)
admin.site.register(Lesson)
admin.site.register(LessonProgress)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(TestResult)