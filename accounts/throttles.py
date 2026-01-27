from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


class ResendVerificationRateThrottle(UserRateThrottle):
    scope = "resend_verification"
