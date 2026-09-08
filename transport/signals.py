from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TransportHandover
from parcels.models import Parcel
from tracking.models import TrackingEvent


@receiver(post_save, sender=TransportHandover)
def handle_transport_handover_status(sender, instance, created, **kwargs):
    parcel = instance.parcel

    # --------------------------------------------------
    # 1. PARCEL RECEIVED AT ORIGIN
    # --------------------------------------------------
    if instance.status == "AT_ORIGIN":

        if parcel.status != Parcel.Status.AT_ORIGIN:
            parcel.status = Parcel.Status.AT_ORIGIN
            parcel.save(update_fields=["status"])

            TrackingEvent.objects.create(
                parcel=parcel,
                event_type="AT_ORIGIN",
                location=instance.transport_route.origin,
                notes=(
                    f"Parcel received at origin for transport with "
                    f"{instance.transport_route.transport_company.name}."
                )
            )

    # --------------------------------------------------
    # 2. PARCEL IN TRANSIT
    # --------------------------------------------------
    elif instance.status == "IN_TRANSIT":

        if parcel.status != Parcel.Status.IN_TRANSIT:
            parcel.status = Parcel.Status.IN_TRANSIT
            parcel.save(update_fields=["status"])

            TrackingEvent.objects.create(
                parcel=parcel,
                event_type="IN_TRANSIT",
                location=instance.transport_route.origin,
                notes=(
                    f"Parcel dispatched from "
                    f"{instance.transport_route.origin} to "
                    f"{instance.transport_route.destination} with "
                    f"{instance.transport_route.transport_company.name}."
                )
            )

    # --------------------------------------------------
    # 3. PARCEL ARRIVED AT DESTINATION
    # --------------------------------------------------
    elif instance.status == "AT_DESTINATION":

        if parcel.status != Parcel.Status.AT_DESTINATION:
            parcel.status = Parcel.Status.AT_DESTINATION
            parcel.save(update_fields=["status"])

            TrackingEvent.objects.create(
                parcel=parcel,
                event_type="AT_DESTINATION",
                location=instance.transport_route.destination,
                notes=(
                    f"Parcel arrived at "
                    f"{instance.transport_route.destination} and is ready "
                    f"for final delivery."
                )
            )