from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # All API routes grouped cleanly
    path("api/", include("accounts.urls")),
    path("api/", include("courses.urls")),
]
