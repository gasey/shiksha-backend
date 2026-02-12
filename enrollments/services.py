from .models import Enrollment


def is_user_enrolled(*, user, course) -> bool:
    return Enrollment.objects.filter(
        user=user,
        course=course,
        status=Enrollment.STATUS_ACTIVE
    ).exists()
