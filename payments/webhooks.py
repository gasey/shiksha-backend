import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from payments.models import Order, Payment
from enrollments.models import Enrollment
from accounts.models import Role, UserRole


@csrf_exempt
def razorpay_webhook(request):
    signature = request.headers.get("X-Razorpay-Signature")
    body = request.body

    expected = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        return HttpResponse(status=400)

    payload = json.loads(body)
    event = payload.get("event")

    if event == "payment.captured":
        payment_data = payload["payload"]["payment"]["entity"]
        order_id = payment_data["order_id"]

        order = Order.objects.select_for_update().get(
            razorpay_order_id=order_id
        )

        # Idempotency guard
        if hasattr(order, "payment"):
            return HttpResponse(status=200)

        Payment.objects.create(
            order=order,
            razorpay_payment_id=payment_data["id"],
            status=Payment.STATUS_SUCCESS,
            raw_payload=payload,
        )

        order.status = Order.STATUS_PAID
        order.save()

        Enrollment.objects.get_or_create(
            user=order.user,
            course=order.course,
            defaults={"status": Enrollment.STATUS_ACTIVE},
        )

        # Role switch (GUEST → STUDENT)
        UserRole.objects.filter(user=order.user, is_active=True).update(is_active=False)
        student_role = Role.objects.get(name="STUDENT")
        UserRole.objects.update_or_create(
            user=order.user,
            role=student_role,
            defaults={"is_active": True},
        )

    return HttpResponse(status=200)
