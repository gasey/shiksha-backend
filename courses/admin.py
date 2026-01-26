from django.contrib import admin
from .models import Course, CourseDetail


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "created_at")
    search_fields = ("title",)
    list_filter = ("created_at",)


@admin.register(CourseDetail)
class CourseDetailAdmin(admin.ModelAdmin):
    list_display = ("course", "subject", "level", "duration_weeks")

