import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from agents.models import Agent
from deliveries.models import DeliveryAssignment
from parcels.models import Parcel


class Payment(models.Model):

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
        CARD = "CARD", "Card"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"

    class PaymentTiming(models.TextChoices):
        BEFORE_PICKUP = "BEFORE_PICKUP", "Pay Before Pickup"
        ON_DELIVERY = "ON_DELIVERY", "Pay on Delivery"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_timing = models.CharField(
        max_length=20,
        choices=PaymentTiming.choices,
        default=PaymentTiming.BEFORE_PICKUP
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    transaction_reference = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def clean(self):
        super().clean()

        errors = {}

        # 1. PAYMENT AMOUNT MUST BE POSITIVE
        if self.amount is not None and self.amount <= 0:
            errors["amount"] = (
                "Payment amount must be greater than zero."
            )

        # 2. PAYMENT MUST MATCH PARCEL DELIVERY FEE
        if self.parcel_id and self.amount is not None:
            expected_amount = self.parcel.delivery_fee

            if self.amount != expected_amount:
                errors["amount"] = (
                    f"Payment amount must match the parcel delivery fee "
                    f"of UGX {expected_amount:,.2f}."
                )

        # 3. PREVENT DUPLICATE ACTIVE PAYMENTS
        if (
            self.parcel_id
            and self.status in [
                self.Status.PENDING,
                self.Status.PAID,
            ]
        ):
            duplicate_payment = Payment.objects.filter(
                parcel=self.parcel,
                status__in=[
                    self.Status.PENDING,
                    self.Status.PAID,
                ],
            ).exclude(pk=self.pk)

            if duplicate_payment.exists():
                errors["parcel"] = (
                    "This parcel already has a pending or paid payment."
                )

        # 4. PAYMENT METHOD REQUIRED BEFORE MARKING AS PAID
        if (
            self.status == self.Status.PAID
            and not self.payment_method
        ):
            errors["payment_method"] = (
                "Please select a payment method before marking "
                "this payment as paid."
            )

        # 5. PAYMENT STATUS TRANSITION VALIDATION
        if self.pk:
            try:
                previous = Payment.objects.get(pk=self.pk)
            except Payment.DoesNotExist:
                previous = None

            if previous and previous.status != self.status:
                allowed_transitions = {
                    self.Status.PENDING: [
                        self.Status.PAID,
                        self.Status.FAILED,
                    ],
                    self.Status.FAILED: [
                        self.Status.PENDING,
                    ],
                    self.Status.PAID: [
                        self.Status.REFUNDED,
                    ],
                    self.Status.REFUNDED: [],
                }

                allowed_statuses = allowed_transitions.get(
                    previous.status,
                    []
                )

                if self.status not in allowed_statuses:
                    errors["status"] = (
                        f"Invalid payment status change from "
                        f"{previous.get_status_display()} to "
                        f"{self.get_status_display()}."
                    )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        previous_status = None

        if self.pk:
            try:
                previous_status = (
                    Payment.objects
                    .get(pk=self.pk)
                    .status
                )
            except Payment.DoesNotExist:
                previous_status = None

        if (
            self.status == self.Status.PAID
            and previous_status != self.Status.PAID
            and self.paid_at is None
        ):
            self.paid_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.parcel.tracking_number} - "
            f"{self.amount} - "
            f"{self.status}"
        )


class AgentCommission(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    agent = models.ForeignKey(
        Agent,
        on_delete=models.PROTECT,
        related_name="commissions"
    )

    assignment = models.OneToOneField(
        DeliveryAssignment,
        on_delete=models.PROTECT,
        related_name="commission"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    payment_reference = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def clean(self):
        super().clean()

        errors = {}

        # 1. COMMISSION AMOUNT MUST BE POSITIVE
        if self.amount is not None and self.amount <= 0:
            errors["amount"] = (
                "Commission amount must be greater than zero."
            )

        # 2. AGENT MUST MATCH ASSIGNMENT AGENT
        if self.assignment_id and self.agent_id:
            if self.assignment.agent_id != self.agent_id:
                errors["agent"] = (
                    "The selected agent must be the same agent "
                    "assigned to this delivery assignment."
                )

        # 3. COMMISSION STATUS TRANSITION VALIDATION
        if self.pk:
            try:
                previous = AgentCommission.objects.get(pk=self.pk)
            except AgentCommission.DoesNotExist:
                previous = None

            if previous and previous.status != self.status:
                allowed_transitions = {
                    self.Status.PENDING: [
                        self.Status.APPROVED,
                        self.Status.CANCELLED,
                    ],
                    self.Status.APPROVED: [
                        self.Status.PAID,
                        self.Status.CANCELLED,
                    ],
                    self.Status.PAID: [],
                    self.Status.CANCELLED: [],
                }

                allowed_statuses = allowed_transitions.get(
                    previous.status,
                    []
                )

                if self.status not in allowed_statuses:
                    errors["status"] = (
                        f"Invalid commission status change from "
                        f"{previous.get_status_display()} to "
                        f"{self.get_status_display()}."
                    )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        previous_status = None

        if self.pk:
            try:
                previous_status = (
                    AgentCommission.objects
                    .get(pk=self.pk)
                    .status
                )
            except AgentCommission.DoesNotExist:
                previous_status = None

        now = timezone.now()

        if (
            self.status == self.Status.APPROVED
            and previous_status != self.Status.APPROVED
            and self.approved_at is None
        ):
            self.approved_at = now

        if (
            self.status == self.Status.PAID
            and previous_status != self.Status.PAID
            and self.paid_at is None
        ):
            self.paid_at = now

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.agent.agent_code} - "
            f"{self.amount} - "
            f"{self.status}"
        )