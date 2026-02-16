from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from django.db import transaction

from .models import User, Profile, Role, UserRole


# ===============================
# READ SERIALIZER (For /me/)
# ===============================
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    avatar_type = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "full_name",
            "email",
            "student_id",
            "phone",
            "avatar_type",
            "avatar",
        ]

    def get_avatar_type(self, obj):
        return obj.avatar_type()

    def get_avatar(self, obj):
        return obj.avatar_value()


# ===============================
# WRITE SERIALIZER (For Updates)
# ===============================
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "full_name",
            "phone",
            "avatar_image",
            "avatar_emoji",
        ]


# ===============================
# UPDATE USER + PROFILE
# ===============================
class UserUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileUpdateSerializer()

    class Meta:
        model = User
        fields = ("username", "profile")

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile
        if profile_data:
            profile = instance.profile

            # Ensure only one avatar type is stored
            if profile_data.get("avatar_image"):
                profile.avatar_emoji = None

            if profile_data.get("avatar_emoji"):
                profile.avatar_image = None

            for attr, value in profile_data.items():
                setattr(profile, attr, value)

            profile.save()

        return instance


# ===============================
# USER ME SERIALIZER
# ===============================
class UserMeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    roles = serializers.SerializerMethodField()
    enrollments = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "profile",
            "roles",
            "enrollments",
        )

    def get_roles(self, obj):
        return [
            user_role.role.name
            for user_role in obj.user_roles.filter(is_active=True)
        ]

    def get_enrollments(self, obj):
        enrollments = obj.enrollments.filter(
            status="ACTIVE"
        ).select_related("course")

        return [
            {
                "id": e.id,
                "course_title": e.course.title,
                "batch_code": e.batch_code,
            }
            for e in enrollments
        ]


# ===============================
# SIGNUP
# ===============================
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "username", "password")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError("Email is already registered.")
        return value.lower()

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise ValidationError("Username is already taken.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"].lower(),
            username=validated_data["username"],
            password=validated_data["password"],
        )

        user.is_verified = False
        user.save(update_fields=["is_verified"])

        guest_role, _ = Role.objects.get_or_create(name="GUEST")

        UserRole.objects.create(
            user=user,
            role=guest_role,
            is_active=True,
        )

        return user
