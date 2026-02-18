from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Assignment, AssignmentSubmission
from .serializers import (
    AssignmentListSerializer,
    AssignmentDetailSerializer,
)
from enrollments.models import Enrollment


def student_enrolled_in_subject(user, subject_id):
    return Enrollment.objects.filter(
        user=user,
        course__subjects__id=subject_id,
        status="ACTIVE"
    ).exists()


def student_enrolled_in_assignment(user, assignment):
    return Enrollment.objects.filter(
        user=user,
        course=assignment.chapter.subject.course,
        status="ACTIVE"
    ).exists()


class SubjectAssignmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):

        if not student_enrolled_in_subject(request.user, subject_id):
            return Response(
                {"detail": "Not enrolled."},
                status=status.HTTP_403_FORBIDDEN
            )

        assignments = (
            Assignment.objects
            .filter(chapter__subject__id=subject_id)
            .select_related("chapter")
        )

        serializer = AssignmentListSerializer(
            assignments,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


class AssignmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assignment_id):
        assignment = get_object_or_404(
            Assignment.objects.select_related(
                "chapter__subject__course"
            ),
            id=assignment_id
        )

        if not student_enrolled_in_assignment(request.user, assignment):
            return Response(
                {"detail": "Not authorized."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AssignmentDetailSerializer(
            assignment,
            context={"request": request}
        )

        return Response(serializer.data)


class SubmitAssignmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, assignment_id):

        assignment = get_object_or_404(
            Assignment.objects.select_related(
                "chapter__subject__course"
            ),
            id=assignment_id
        )

        if not student_enrolled_in_assignment(request.user, assignment):
            return Response(
                {"detail": "Not authorized."},
                status=status.HTTP_403_FORBIDDEN
            )

        if assignment.is_expired:
            return Response(
                {"detail": "Assignment expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES.get("file")

        if not file:
            return Response(
                {"detail": "File required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        AssignmentSubmission.objects.update_or_create(
            assignment=assignment,
            student=request.user,
            defaults={"submitted_file": file},
        )

        return Response(
            {"detail": "Submission successful."},
            status=status.HTTP_200_OK
        )
