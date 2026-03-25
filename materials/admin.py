from django.contrib import admin
from .models import StudyMaterial, MaterialFile


class MaterialFileInline(admin.TabularInline):
    model = MaterialFile
    extra = 1


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):

    list_display = ("title", "chapter", "uploaded_by", "created_at")

    search_fields = ("title",)

    inlines = [MaterialFileInline]
