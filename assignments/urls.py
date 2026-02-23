from django.urls import path
from .views import (
    CourseAssignmentsView,
    SubjectAssignmentsView,
    AssignmentDetailView,
    SubmitAssignmentView,
)

urlpatterns = [
    path(
        "courses/<uuid:course_id>/",
        CourseAssignmentsView.as_view(),
    ),
    path(
        "subjects/<uuid:subject_id>/",
        SubjectAssignmentsView.as_view(),
    ),
    path(
        "<uuid:assignment_id>/",
        AssignmentDetailView.as_view(),
    ),
    path(
        "<uuid:assignment_id>/submit/",
        SubmitAssignmentView.as_view(),
    ),
]
