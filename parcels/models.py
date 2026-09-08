import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from transport.models import Location, TransportRoute


class TrackingSequence(models.Model):
    year = models.PositiveIntegerField(
        unique=True
    )

    last_number = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return f"{self.year} - {self.last_number}"


class Parcel(models.Model):

    class DeliveryType(models.TextChoices):
        NORMAL = "NORMAL", "Normal Delivery"
        EXPRESS = "EXPRESS", "Express Delivery"

    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        AWAITING_PICKUP = "AWAITING_PICKUP", "Awaiting Pickup"
        PICKED_UP = "PICKED_UP", "Picked Up"
        AT_ORIGIN = "AT_ORIGIN", "At Origin"
        IN_TRANSIT = "IN_TRANSIT", "In Transit"
        AT_DESTINATION = "AT_DESTINATION", "At Destination"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for Delivery"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    tracking_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_parcels"
    )

    recipient_name = models.CharField(
        max_length=150
    )

    recipient_phone = models.CharField(
        max_length=20
    )

    recipient_email = models.EmailField(
        blank=True
    )

    pickup_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="pickup_parcels"
    )

    destination_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="destination_parcels"
    )

    transport_route = models.ForeignKey(
        TransportRoute,
        on_delete=models.PROTECT,
        related_name="parcels",
        null=True,
        blank=True
    )

    description = models.TextField()

    weight_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    declared_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    delivery_type = models.CharField(
        max_length=10,
        choices=DeliveryType.choices,
        default=DeliveryType.NORMAL
    )

    delivery_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        editable=False
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.CREATED
    )

    special_instructions = models.TextField(
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

        # Pickup and destination must not be the same
        if (
            self.pickup_location_id
            and self.destination_location_id
            and self.pickup_location_id == self.destination_location_id
        ):
            errors["destination_location"] = (
                "Destination location cannot be the same as pickup location."
            )

        # Every parcel must have a transport route
        if not self.transport_route_id:
            errors["transport_route"] = (
                "Please select a transport route for this parcel."
            )

        else:
            route = self.transport_route

            # Route must be active
            if not route.is_active:
                errors["transport_route"] = (
                    "The selected transport route is not active."
                )

            # Route origin must match parcel pickup location
            if (
                self.pickup_location_id
                and route.origin_id != self.pickup_location_id
            ):
                errors["transport_route"] = (
                    "The selected route origin does not match "
                    "the parcel pickup location."
                )

            # Route destination must match parcel destination
            if (
                self.destination_location_id
                and route.destination_id != self.destination_location_id
            ):
                errors["transport_route"] = (
                    "The selected route destination does not match "
                    "the parcel destination location."
                )

        if errors:
            raise ValidationError(errors)

    def calculate_delivery_fee(self):
        if not self.transport_route:
            return 0

        if self.delivery_type == self.DeliveryType.EXPRESS:
            return self.transport_route.express_delivery_fee

        return self.transport_route.normal_delivery_fee

    def generate_tracking_number(self):
        year = timezone.now().year

        with transaction.atomic():
            sequence, _ = (
                TrackingSequence.objects
                .select_for_update()
                .get_or_create(year=year)
            )

            sequence.last_number += 1
            sequence.save(
                update_fields=["last_number"]
            )

            return f"DS-{year}-{sequence.last_number:06d}"

    def save(self, *args, **kwargs):
        # Generate tracking number automatically
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()

        # Calculate delivery fee automatically
        if self.transport_route_id:
            self.delivery_fee = self.calculate_delivery_fee()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_number} - {self.recipient_name}"