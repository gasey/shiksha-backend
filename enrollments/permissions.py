from rest_framework.permissions import BasePermission
from .models import Enrollment


class IsEnrolled(BasePermission):
    """
    Requires course_id in URL kwargs or request.data
    """

    def has_permission(self, request, view):
        course_id = (
            view.kwargs.get("course_id")
            or request.data.get("course")
        )

        if not course_id or not request.user.is_authenticated:
            return False

        return Enrollment.objects.filter(
            user=request.user,
            course_id=course_id,
            status=Enrollment.STATUS_ACTIVE
        ).exists()
