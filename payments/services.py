import razorpay
from django.conf import settings
from .models import Order


client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


def create_order(*, user, course):
    rp_order = client.order.create({
        "amount": course.price * 100,
        "currency": "INR",
        "payment_capture": 1,
    })

    return Order.objects.create(
        user=user,
        course=course,
        razorpay_order_id=rp_order["id"],
        amount=course.price * 100,
        status=Order.STATUS_CREATED,
    )
