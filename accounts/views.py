import jwt
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny,
)
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore

from accounts.audit import log_auth_event
from accounts.models import AuthEvent, User, Role, UserRole
from accounts.throttles import LoginRateThrottle, ResendVerificationRateThrottle
from accounts.email_tokens import (
    generate_email_verification_token,
    decode_email_verification_token,
)

from .serializers import (
    SignupSerializer,
    UserMeSerializer,
    UserUpdateSerializer,
)
from .permissions import IsEmailVerified


# 🔒 VERIFIED USERS ONLY
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


# 📝 SIGNUP — PUBLIC, NO JWT
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        user.is_verified = False
        user.save(update_fields=["is_verified"])

        token = generate_email_verification_token(user)
        verify_link = f"https://shikshacom.com/verify-email?token={token}"

        send_mail(
            subject="Verify your email",
            message=f"Click to verify your email:\n{verify_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response(
            {
                "detail": "Signup successful. Please verify your email.",
                "user": UserMeSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


# 🔑 LOGIN — JWT ISSUED ONLY IF VERIFIED
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


# ✅ EMAIL VERIFICATION
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            raise ValidationError("Verification token is required.")

        try:
            payload = decode_email_verification_token(token)
            if payload.get("type") != "email_verification":
                raise ValidationError("Invalid token type.")

            user = User.objects.get(id=payload["sub"])

            if user.is_verified:
                return Response({"detail": "Email already verified."})

            user.is_verified = True
            user.verified_at = timezone.now()
            user.save(update_fields=["is_verified", "verified_at"])

            log_auth_event(
                request,
                AuthEvent.EVENT_VERIFY_EMAIL_SUCCESS,
                user=user,
            )

            return Response({"detail": "Email verified successfully."})

        except jwt.ExpiredSignatureError:
            log_auth_event(request, AuthEvent.EVENT_VERIFY_EMAIL_FAILED)
            raise ValidationError("Verification token expired.")
        except jwt.InvalidTokenError:
            log_auth_event(request, AuthEvent.EVENT_VERIFY_EMAIL_FAILED)
            raise ValidationError("Invalid verification token.")


# 🔁 RESEND VERIFICATION EMAIL
class ResendVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ResendVerificationRateThrottle]

    def post(self, request):
        user = request.user
        if user.is_verified:
            raise ValidationError("Email already verified.")

        token = generate_email_verification_token(user)
        verify_link = f"https://shikshacom.com/verify-email?token={token}"

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
