import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Location(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    district = models.CharField(
        max_length=100
    )

    town = models.CharField(
        max_length=100
    )

    address = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.town}, {self.district}"


class TransportCompany(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=150,
        unique=True
    )

    contact_person = models.CharField(
        max_length=150,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class TransportRoute(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    transport_company = models.ForeignKey(
        TransportCompany,
        on_delete=models.PROTECT,
        related_name="routes"
    )

    origin = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="routes_from"
    )

    destination = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="routes_to"
    )

    normal_delivery_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    express_delivery_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    estimated_normal_hours = models.PositiveIntegerField()

    estimated_express_hours = models.PositiveIntegerField()

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.transport_company.name}: "
            f"{self.origin} → {self.destination}"
        )


class TransportHandover(models.Model):

    class Status(models.TextChoices):
        AT_ORIGIN = "AT_ORIGIN", "At Origin"
        IN_TRANSIT = "IN_TRANSIT", "In Transit"
        AT_DESTINATION = "AT_DESTINATION", "At Destination"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    parcel = models.OneToOneField(
        "parcels.Parcel",
        on_delete=models.CASCADE,
        related_name="transport_handover"
    )

    transport_route = models.ForeignKey(
        TransportRoute,
        on_delete=models.PROTECT,
        related_name="handovers"
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.AT_ORIGIN
    )

    received_at_origin_at = models.DateTimeField(
        null=True,
        blank=True
    )

    dispatched_at = models.DateTimeField(
        null=True,
        blank=True
    )

    arrived_at_destination_at = models.DateTimeField(
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

        if self.pk:
            try:
                previous = TransportHandover.objects.get(pk=self.pk)
            except TransportHandover.DoesNotExist:
                previous = None

            if previous and previous.status != self.status:

                allowed_transitions = {
                    self.Status.AT_ORIGIN: [
                        self.Status.IN_TRANSIT,
                    ],
                    self.Status.IN_TRANSIT: [
                        self.Status.AT_DESTINATION,
                    ],
                    self.Status.AT_DESTINATION: [],
                }

                allowed_statuses = allowed_transitions.get(
                    previous.status,
                    []
                )

                if self.status not in allowed_statuses:
                    errors["status"] = (
                        f"Invalid transport status change from "
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
                    TransportHandover.objects
                    .get(pk=self.pk)
                    .status
                )
            except TransportHandover.DoesNotExist:
                previous_status = None

        now = timezone.now()

        if (
            self.status == self.Status.AT_ORIGIN
            and previous_status != self.Status.AT_ORIGIN
            and self.received_at_origin_at is None
        ):
            self.received_at_origin_at = now

        if (
            self.status == self.Status.IN_TRANSIT
            and previous_status != self.Status.IN_TRANSIT
            and self.dispatched_at is None
        ):
            self.dispatched_at = now

        if (
            self.status == self.Status.AT_DESTINATION
            and previous_status != self.Status.AT_DESTINATION
            and self.arrived_at_destination_at is None
        ):
            self.arrived_at_destination_at = now

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.parcel.tracking_number} - "
            f"{self.get_status_display()}"
        )