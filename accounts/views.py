from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserMeSerializer
from rest_framework.permissions import IsAdminUser

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
from .serializers import SignupSerializer, UserMeSerializer, UserMeSerializer, UserUpdateSerializer
from rest_framework.exceptions import ValidationError
from accounts.models import Role, UserRole


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(UserMeSerializer(request.user).data)


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserMeSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class RequestTeacherRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.has_role("teacher"):
            raise ValidationError("You are already a teacher.")

        teacher_role = Role.objects.get(name="teacher")

        # Prevent duplicate requests
        if UserRole.objects.filter(user=user, role=teacher_role).exists():
            raise ValidationError("Teacher role already requested.")

        UserRole.objects.create(
            user=user,
            role=teacher_role,
            is_active=False,   # 🔒 pending approval
        )

        return Response(
            {"detail": "Teacher role request submitted."},
            status=201,
        )


class ApproveTeacherRoleView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            raise ValidationError("user_id is required.")

        teacher_role = Role.objects.get(name="teacher")

        try:
            user_role = UserRole.objects.get(
                user__id=user_id,
                role=teacher_role,
                is_active=False,
            )
        except UserRole.DoesNotExist:
            raise ValidationError("No pending teacher request found.")

        user_role.approve(admin_user=request.user)

        return Response(
            {"detail": "Teacher role approved."},
            status=200,
        )
