from rest_framework import serializers
from .models import Course
from .models import Subject


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class SubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(
        source="course.teacher.username", read_only=True)

    class Meta:
        model = Subject
        fields = (
            "id",
            "name",
            "order",
            "teacher_name",
        )
