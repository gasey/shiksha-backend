import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    chapter = models.ForeignKey(
        "courses.Chapter",
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    attachment = models.FileField(
        upload_to="assignments/files/",
        null=True,
        blank=True,
    )

    due_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["chapter"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        return timezone.now() > self.due_date


class AssignmentSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
    )

    submitted_file = models.FileField(
        upload_to="assignments/submissions/"
    )

    submitted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("assignment", "student")
        indexes = [
            models.Index(fields=["assignment", "student"]),
        ]

    def __str__(self):
        return f"{self.student.email} → {self.assignment.title}"
