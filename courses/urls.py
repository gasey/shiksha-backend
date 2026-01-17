from django.urls import path

# update
from .views import (
    CreateCourseView,
    MyCoursesView,
    UpdateCourseView,
    DeleteCourseView,
)

urlpatterns = [
    path("courses/", CreateCourseView.as_view(), name="create-course"),
    path("courses/mine/", MyCoursesView.as_view(), name="my-courses"),

    # update
    path("courses/<uuid:course_id>/", UpdateCourseView.as_view()),
    path("courses/<uuid:course_id>/delete/", DeleteCourseView.as_view()),
]
