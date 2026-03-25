from django.contrib import admin
from .models import Course, Subject, Chapter, SubjectTeacher
from .models_recordings import SessionRecording


# =========================
# COURSE ADMIN
# =========================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
    list_filter = ("created_at",)


# =========================
# SUBJECT TEACHER INLINE
# =========================

class SubjectTeacherInline(admin.TabularInline):
    model = SubjectTeacher
    extra = 1


# =========================
# SESSION RECORDING INLINE
# =========================

class SessionRecordingInline(admin.TabularInline):
    model = SessionRecording
    extra = 1
    fields = (
        "title",
        "chapter",
        "session_date",
        "duration_seconds",
        "bunny_video_id",
        "is_published",
    )


# =========================
# SUBJECT ADMIN
# =========================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "order", "get_teachers")
    list_filter = ("course",)
    ordering = ("course", "order")
    search_fields = ("name", "course__title")

    inlines = [
        SubjectTeacherInline,
        SessionRecordingInline,  # 👈 recordings appear inside subject
    ]

    def get_teachers(self, obj):
        return ", ".join(
            [st.teacher.email for st in obj.subject_teachers.all()]
        )

    get_teachers.short_description = "Teachers"


# =========================
# CHAPTER ADMIN
# =========================

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "order")
    list_filter = ("subject",)
    ordering = ("subject", "order")


# =========================
# SESSION RECORDING ADMIN
# =========================

@admin.register(SessionRecording)
class SessionRecordingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subject",
        "chapter",
        "session_date",
        "is_published",
        "uploaded_by",
    )
    list_filter = ("subject", "is_published")
    search_fields = ("title", "subject__name")
    ordering = ("-session_date",)
    readonly_fields = ("created_at",)
