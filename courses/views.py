from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.permissions import IsTeacher
from .models import Course
from .serializers import CourseSerializer

# update
from django.shortcuts import get_object_or_404


# Create Course (Teacher Only)


class CreateCourseView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = serializer.save(teacher=request.user)

        return Response(
            CourseSerializer(course).data,
            status=status.HTTP_201_CREATED,
        )


# LIST OWN COURSES
class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        courses = Course.objects.filter(teacher=request.user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

# new


class UpdateCourseView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def patch(self, request, course_id):
        course = get_object_or_404(
            Course,
            id=course_id,
            teacher=request.user,  # 🔐 ownership enforced
        )

        serializer = CourseSerializer(
            course,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class DeleteCourseView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def delete(self, request, course_id):
        course = get_object_or_404(
            Course,
            id=course_id,
            teacher=request.user,  # 🔐 ownership enforced
        )

        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
