from django.urls import path
from .webhooks import razorpay_webhook

urlpatterns = [
    path("webhook/", razorpay_webhook),
    path("api/payments/", include("payments.urls"))
]
