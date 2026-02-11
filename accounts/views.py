from rest_framework import status

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import authenticate
from django.shortcuts import redirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore

from accounts.audit import log_auth_event
from accounts.models import (
    AuthEvent,
    User,
    EmailVerificationToken,
    Role,
    UserRole,
)
from accounts.throttles import (
    LoginRateThrottle,
    ResendVerificationRateThrottle,
)

from .serializers import (
    SignupSerializer,
    UserMeSerializer,
    UserUpdateSerializer,
)
from .permissions import IsEmailVerified


#  VERIFIED USERS ONLY
class MeView(APIView):
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get(self, request):
        return Response(UserMeSerializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserMeSerializer(request.user).data)


#  SIGNUP — PUBLIC, NO JWT
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        user.is_verified = False
        user.save(update_fields=["is_verified"])

        token = EmailVerificationToken.generate(user)

        verify_link = f"https://api.shikshacom.com/api/verify-email/?token={token.token}"

        # Email sending disabled for now (OK)
        # send_mail(
        #     subject="Verify your email",
        #     message=f"Click to verify your email:\n{verify_link}",
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[user.email],
        # )

        return Response(
            {"detail": "Signup successful. Please verify your email."},
            status=status.HTTP_201_CREATED,
        )


#  LOGIN — JWT ISSUED ONLY IF VERIFIED
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            raise ValidationError("Email and password are required.")

        user = authenticate(request, email=email, password=password)

        if not user:
            log_auth_event(request, AuthEvent.EVENT_LOGIN_FAILED)
            raise ValidationError("Invalid credentials.")

        if not user.is_verified:
            log_auth_event(
                request,
                AuthEvent.EVENT_LOGIN_BLOCKED_UNVERIFIED,
                user=user,
            )
            raise ValidationError("Email not verified.")

        refresh = RefreshToken.for_user(user)

        log_auth_event(
            request,
            AuthEvent.EVENT_LOGIN_SUCCESS,
            user=user,
        )

        return Response(
            {
                "user": UserMeSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


# ✅ EMAIL VERIFICATION — GET + REDIRECT
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token_value = request.query_params.get("token")

        try:
            token = EmailVerificationToken.objects.select_related("user").get(
                token=token_value,
                expires_at__gt=timezone.now(),
            )
        except EmailVerificationToken.DoesNotExist:
            log_auth_event(request, AuthEvent.EVENT_VERIFY_EMAIL_FAILED)
            return redirect(
                "https://shikshacom.com/email-verified?status=failed"
            )

        user = token.user

        if not user.is_verified:
            user.is_verified = True
            user.verified_at = timezone.now()
            user.save(update_fields=["is_verified", "verified_at"])

        token.delete()

        log_auth_event(
            request,
            AuthEvent.EVENT_VERIFY_EMAIL_SUCCESS,
            user=user,
        )

        return redirect(
            "https://shikshacom.com/email-verified?status=success"
        )


# 🔁 RESEND VERIFICATION EMAIL — PUBLIC
class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ResendVerificationRateThrottle]

    def post(self, request):
        email = request.data.get("email")

        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError("User not found.")

        if user.is_verified:
            raise ValidationError("Email already verified.")

        token = EmailVerificationToken.generate(user)

        verify_link = (
            f"https://api.shikshacom.com/api/verify-email/"
            f"?token={token.token}"
        )

        send_mail(
            subject="Verify your email",
            message=f"Click to verify your email:\n{verify_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        log_auth_event(
            request,
            AuthEvent.EVENT_RESEND_VERIFICATION,
            user=user,
        )

        return Response({"detail": "Verification email resent."})


class RequestTeacherRoleView(APIView):
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def post(self, request):
        user = request.user

        if user.has_role("teacher"):
            raise ValidationError("You are already a teacher.")

        teacher_role = Role.objects.get(name="teacher")

        if UserRole.objects.filter(user=user, role=teacher_role).exists():
            raise ValidationError("Teacher role already requested.")

        UserRole.objects.create(
            user=user,
            role=teacher_role,
            is_active=False,
        )

        return Response(
            {"detail": "Teacher role request submitted."},
            status=status.HTTP_201_CREATED,
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
            status=status.HTTP_200_OK,
        )
