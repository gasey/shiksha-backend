from django.urls import path
from .views import (
    MeView,
    SignupView,
    RequestTeacherRoleView,
    ApproveTeacherRoleView,
)


urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("roles/request-teacher/",
         RequestTeacherRoleView.as_view(), name="request-teacher"),
    path("roles/approve-teacher/",
         ApproveTeacherRoleView.as_view(), name="approve-teacher"),



]
