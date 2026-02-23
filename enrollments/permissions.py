from rest_framework.permissions import BasePermission
from .models import Enrollment


class IsEnrolledInCourse(BasePermission):

    def has_permission(self, request, view):
        course_id = view.kwargs.get("course_id")

        if not course_id:
            return True

        return Enrollment.objects.filter(
            user=request.user,
            course__id=course_id,
            status="ACTIVE"
        ).exists()
