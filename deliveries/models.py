import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from agents.models import Agent
from parcels.models import Parcel


class DeliveryAssignment(models.Model):

    class AssignmentType(models.TextChoices):
        PICKUP = "PICKUP", "Pickup"
        DELIVERY = "DELIVERY", "Final Delivery"

    class Status(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        ACCEPTED = "ACCEPTED", "Accepted"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    agent = models.ForeignKey(
        Agent,
        on_delete=models.PROTECT,
        related_name="delivery_assignments"
    )

    assignment_type = models.CharField(
        max_length=20,
        choices=AssignmentType.choices
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ASSIGNED
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    notes = models.TextField(
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

        # 1. PREVENT DUPLICATE ACTIVE/COMPLETED ASSIGNMENTS
        if self.parcel_id and self.assignment_type:
            blocking_statuses = [
                self.Status.ASSIGNED,
                self.Status.ACCEPTED,
                self.Status.IN_PROGRESS,
                self.Status.COMPLETED,
            ]

            duplicate = DeliveryAssignment.objects.filter(
                parcel=self.parcel,
                assignment_type=self.assignment_type,
                status__in=blocking_statuses,
            ).exclude(pk=self.pk)

            if duplicate.exists():
                errors["assignment_type"] = (
                    "This parcel already has an assignment of this type "
                    "that is active or completed."
                )

        # 2. PAY BEFORE PICKUP VALIDATION
        if (
            self.parcel_id
            and self.assignment_type == self.AssignmentType.PICKUP
            and self.status == self.Status.IN_PROGRESS
        ):
            payment = (
                self.parcel.payments
                .filter(
                    status__in=[
                        "PENDING",
                        "PAID",
                    ]
                )
                .order_by("-created_at")
                .first()
            )

            if payment:
                if (
                    payment.payment_timing == "BEFORE_PICKUP"
                    and payment.status != "PAID"
                ):
                    errors["status"] = (
                        "This parcel requires payment before pickup. "
                        "Please mark the payment as paid before starting pickup."
                    )

        # 3. STATUS TRANSITION VALIDATION
        if self.pk:
            try:
                previous = DeliveryAssignment.objects.get(pk=self.pk)
            except DeliveryAssignment.DoesNotExist:
                previous = None

            if previous and previous.status != self.status:
                allowed_transitions = {
                    self.Status.ASSIGNED: [
                        self.Status.ACCEPTED,
                        self.Status.REJECTED,
                        self.Status.CANCELLED,
                    ],
                    self.Status.ACCEPTED: [
                        self.Status.IN_PROGRESS,
                        self.Status.CANCELLED,
                    ],
                    self.Status.IN_PROGRESS: [
                        self.Status.COMPLETED,
                        self.Status.CANCELLED,
                    ],
                    self.Status.COMPLETED: [],
                    self.Status.REJECTED: [],
                    self.Status.CANCELLED: [],
                }

                allowed_statuses = allowed_transitions.get(
                    previous.status,
                    []
                )

                if self.status not in allowed_statuses:
                    errors["status"] = (
                        f"Invalid status change from "
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
                    DeliveryAssignment.objects
                    .get(pk=self.pk)
                    .status
                )
            except DeliveryAssignment.DoesNotExist:
                previous_status = None

        if (
            self.status == self.Status.ACCEPTED
            and previous_status != self.Status.ACCEPTED
            and self.accepted_at is None
        ):
            self.accepted_at = timezone.now()

        if (
            self.status == self.Status.IN_PROGRESS
            and previous_status != self.Status.IN_PROGRESS
            and self.started_at is None
        ):
            self.started_at = timezone.now()

        if (
            self.status == self.Status.COMPLETED
            and previous_status != self.Status.COMPLETED
            and self.completed_at is None
        ):
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.assignment_type} - "
            f"{self.parcel.tracking_number} - "
            f"{self.agent.agent_code}"
        )