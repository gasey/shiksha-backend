from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # All API routes grouped cleanly
    path("api/", include("accounts.urls")),
    path("api/", include("courses.urls")),
    path("api/", include("assignments.urls")),
    path("courses/", include("courses.urls")),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
