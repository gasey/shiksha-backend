from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Role, UserRole
from courses.models import Course, Subject, Chapter
from payments.models import Order, Payment
from enrollments.models import Enrollment
from assignments.models import Assignment, AssignmentSubmission


# =========================
# USER ADMIN
# =========================

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "email",
        "username",
        "is_verified",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_verified",
        "is_staff",
        "is_active",
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("username",)}),
        ("Verification", {"fields": ("is_verified", "verified_at")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    ordering = ("email",)
    search_fields = ("email", "username")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)


admin.site.register(Role)
admin.site.register(UserRole)


# =========================
# COURSE ADMIN
# =========================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "created_at")
    search_fields = ("title",)
    list_filter = ("created_at",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "order")
    list_filter = ("course",)
    ordering = ("course", "order")


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "order")
    list_filter = ("subject",)
    ordering = ("subject", "order")


# =========================
# PAYMENT ADMIN
# =========================

admin.site.register(Order)
admin.site.register(Payment)


# =========================
# ENROLLMENT ADMIN
# =========================

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "enrolled_at")
    list_filter = ("status", "enrolled_at")
    search_fields = ("user__email", "course__title")


# =========================
# ASSIGNMENT ADMIN
# =========================

class AssignmentSubmissionInline(admin.TabularInline):
    model = AssignmentSubmission
    extra = 0
    readonly_fields = ("student", "submitted_file", "submitted_at")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "chapter",
        "due_date",
        "created_at",
    )
    list_filter = (
        "due_date",
        "chapter__subject__course",
    )
    search_fields = (
        "title",
        "chapter__subject__name",
        "chapter__subject__course__title",
    )
    ordering = ("-created_at",)
    inlines = [AssignmentSubmissionInline]


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "assignment",
        "student",
        "submitted_at",
    )
    list_filter = (
        "submitted_at",
        "assignment__chapter__subject__course",
    )
    search_fields = (
        "student__email",
        "assignment__title",
    )
    ordering = ("-submitted_at",)
