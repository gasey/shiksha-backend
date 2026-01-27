from django.urls import path
from .views import (
    MeView,
    SignupView,
    LoginView,
    VerifyEmailView,
    ResendVerificationEmailView,
    RequestTeacherRoleView,
    ApproveTeacherRoleView,
)

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),

    # ✅ Email verification
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path(
        "resend-verification/",
        ResendVerificationEmailView.as_view(),
        name="resend-verification",
    ),

    # ✅ Roles
    path(
        "roles/request-teacher/",
        RequestTeacherRoleView.as_view(),
        name="request-teacher",
    ),
    path(
        "roles/approve-teacher/",
        ApproveTeacherRoleView.as_view(),
        name="approve-teacher",
    ),
]
