from django.urls import path
from .views import (
    SubjectAssignmentsView,
    AssignmentDetailView,
    SubmitAssignmentView,
)

urlpatterns = [
    path("subjects/<uuid:subject_id>/", SubjectAssignmentsView.as_view()),
    path("<uuid:assignment_id>/", AssignmentDetailView.as_view()),
    path("<uuid:assignment_id>/submit/", SubmitAssignmentView.as_view()),
]
