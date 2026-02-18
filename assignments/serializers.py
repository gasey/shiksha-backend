from rest_framework import serializers
from .models import Assignment, AssignmentSubmission


class AssignmentListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ("id", "title", "due_date", "status")

    def get_status(self, obj):
        user = self.context["request"].user
        return (
            "SUBMITTED"
            if obj.submissions.filter(student=user).exists()
            else "PENDING"
        )


class AssignmentDetailSerializer(serializers.ModelSerializer):
    submission_status = serializers.SerializerMethodField()
    submitted_file = serializers.SerializerMethodField()
    submitted_at = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "description",
            "attachment",
            "due_date",
            "submission_status",
            "submitted_file",
            "submitted_at",
        )

    def get_submission_status(self, obj):
        user = self.context["request"].user
        submission = obj.submissions.filter(student=user).first()
        return "SUBMITTED" if submission else "PENDING"

    def get_submitted_file(self, obj):
        user = self.context["request"].user
        submission = obj.submissions.filter(student=user).first()
        return submission.submitted_file.url if submission else None

    def get_submitted_at(self, obj):
        user = self.context["request"].user
        submission = obj.submissions.filter(student=user).first()
        return submission.submitted_at if submission else None
