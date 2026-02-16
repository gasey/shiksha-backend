import uuid
import secrets
from django.conf import settings
from django.utils import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def has_role(self, role_name):
        return self.user_roles.filter(
            role__name=role_name,
            is_active=True
        ).exists()


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    student_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    avatar_image = models.ImageField(
        upload_to="avatar/",
        null=True,
        blank=True
    )

    avatar_emoji = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    def avatar_type(self):
        if self.avatar_image:
            return "image"
        if self.avatar_emoji:
            return "emoji"
        return None

    def avatar_value(self):
        if self.avatar_image:
            return self.avatar_image.url
        if self.avatar_emoji:
            return self.avatar_emoji
        return None

    def __str__(self):
        return f"{self.user.email} Profile"

    @property
    def is_complete(self):
        return bool(
            self.full_name
            and self.phone
            and self.user.is_verified
            and self.user.enrollments.filter(status="ACTIVE").exists()
        )


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_roles",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "role")

    def approve(self, admin_user):
        self.is_active = True
        self.approved_by = admin_user
        self.approved_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.user} → {self.role}"


class AuthEvent(models.Model):
    EVENT_LOGIN_SUCCESS = "LOGIN_SUCCESS"
    EVENT_LOGIN_FAILED = "LOGIN_FAILED"
    EVENT_LOGIN_BLOCKED_UNVERIFIED = "LOGIN_BLOCKED_UNVERIFIED"
    EVENT_VERIFY_EMAIL_SUCCESS = "VERIFY_EMAIL_SUCCESS"
    EVENT_VERIFY_EMAIL_FAILED = "VERIFY_EMAIL_FAILED"
    EVENT_RESEND_VERIFICATION = "RESEND_VERIFICATION"

    EVENT_CHOICES = [
        (EVENT_LOGIN_SUCCESS, "Login Success"),
        (EVENT_LOGIN_FAILED, "Login Failed"),
        (EVENT_LOGIN_BLOCKED_UNVERIFIED, "Login Blocked (Unverified)"),
        (EVENT_VERIFY_EMAIL_SUCCESS, "Verify Email Success"),
        (EVENT_VERIFY_EMAIL_FAILED, "Verify Email Failed"),
        (EVENT_RESEND_VERIFICATION, "Resend Verification Email"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="auth_events",
    )

    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} @ {self.created_at}"


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification_tokens",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    @classmethod
    def generate(cls, user):
        return cls.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24),
        )

    def is_expired(self):
        return timezone.now() > self.expires_at
