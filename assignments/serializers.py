from rest_framework import serializers
from .models import Assignment, AssignmentSubmission


class AssignmentListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    subject_name = serializers.CharField(
        source="chapter.subject.name",
        read_only=True
    )
    course_id = serializers.UUIDField(
        source="chapter.subject.course.id",
        read_only=True
    )

    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "due_date",
            "status",
            "subject_name",
            "course_id",
        )

    def get_status(self, obj):
        request = self.context.get("request")
        user = request.user

        submission = getattr(obj, "user_submission", None)

        if submission:
            return "SUBMITTED"

        if obj.due_date < timezone.now():
            return "EXPIRED"

        return "PENDING"


class AssignmentDetailSerializer(serializers.ModelSerializer):
    submission_status = serializers.SerializerMethodField()
    submitted_file = serializers.SerializerMethodField()
    submitted_at = serializers.SerializerMethodField()
    subject_name = serializers.CharField(
        source="chapter.subject.name",
        read_only=True
    )
    course_name = serializers.CharField(
        source="chapter.subject.course.title",
        read_only=True
    )

    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "description",
            "attachment",
            "due_date",
            "subject_name",
            "course_name",
            "submission_status",
            "submitted_file",
            "submitted_at",
        )

    def get_submission(self, obj):
        return getattr(obj, "user_submission", None)

    def get_submission_status(self, obj):
        submission = self.get_submission(obj)

        if submission:
            return "SUBMITTED"

        if obj.due_date < timezone.now():
            return "EXPIRED"

        return "PENDING"

    def get_submitted_file(self, obj):
        submission = self.get_submission(obj)
        if submission and submission.submitted_file:
            return submission.submitted_file.url
        return None

    def get_submitted_at(self, obj):
        submission = self.get_submission(obj)
        return submission.submitted_at if submission else None
