import uuid
from django.db import models
from django.conf import settings


class Enrollment(models.Model):
    STATUS_ACTIVE = "ACTIVE"
    STATUS_REVOKED = "REVOKED"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_REVOKED, "Revoked"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        indexes = [
            models.Index(fields=["user", "course"]),
            models.Index(fields=["status"]),
        ]

    def _str_(self):
        return f"{self.user.email} → {self.course.title}"
