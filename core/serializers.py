from rest_framework import serializers
from .models import Lesson, Test, Question, TestResult, User


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ["correct_option"]  # userga correct javob chiqmaydi


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ["id", "title", "lesson", "questions"]




class TestSubmitSerializer(serializers.Serializer):
    test_id = serializers.IntegerField()
    score = serializers.IntegerField()
    percentage = serializers.FloatField()
    xp_earned = serializers.IntegerField()

    def validate(self, data):
        if data["percentage"] < 0 or data["percentage"] > 100:
            raise serializers.ValidationError("Percentage must be between 0 and 100")

        if data["xp_earned"] < 0:
            raise serializers.ValidationError("XP cannot be negative")

        return data