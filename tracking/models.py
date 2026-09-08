import uuid

from django.conf import settings
from django.db import models

from parcels.models import Parcel
from transport.models import Location


class TrackingEvent(models.Model):

    class EventType(models.TextChoices):
        CREATED = "CREATED", "Parcel Created"
        PICKUP_ASSIGNED = "PICKUP_ASSIGNED", "Pickup Assigned"
        PICKED_UP = "PICKED_UP", "Picked Up"
        AT_ORIGIN = "AT_ORIGIN", "At Origin"
        HANDED_TO_TRANSPORT = "HANDED_TO_TRANSPORT", "Handed to Transport"
        IN_TRANSIT = "IN_TRANSIT", "In Transit"
        AT_DESTINATION = "AT_DESTINATION", "At Destination"
        DELIVERY_ASSIGNED = "DELIVERY_ASSIGNED", "Delivery Assigned"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for Delivery"
        DELIVERED = "DELIVERED", "Delivered"
        FAILED_DELIVERY = "FAILED_DELIVERY", "Failed Delivery"
        RETURNED = "RETURNED", "Returned"
        CANCELLED = "CANCELLED", "Cancelled"
        DAMAGED = "DAMAGED", "Damaged"
        LOST = "LOST", "Lost"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name="tracking_events"
    )

    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tracking_events"
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tracking_updates"
    )

    notes = models.TextField(
        blank=True
    )

    event_time = models.DateTimeField(
        auto_now_add=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["event_time"]

    def __str__(self):
        return (
            f"{self.parcel.tracking_number} - "
            f"{self.event_type}"
        )