from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import Profile
from .models import Role, UserRole


@admin.register(User)
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


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)


admin.site.register(Role)
admin.site.register(UserRole)
