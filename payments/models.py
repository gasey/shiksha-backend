import uuid
from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CREATED = "CREATED"
    STATUS_PAID = "PAID"
    STATUS_FAILED = "FAILED"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Created"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE)

    razorpay_order_id = models.CharField(max_length=100, unique=True)
    amount = models.PositiveIntegerField()  # in paise
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.email} → {self.course.title}"
class Payment(models.Model):
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED = "FAILED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    razorpay_payment_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20)
    raw_payload = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
