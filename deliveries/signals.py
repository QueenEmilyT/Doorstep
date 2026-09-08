from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DeliveryAssignment
from parcels.models import Parcel
from tracking.models import TrackingEvent
from payments.models import AgentCommission


@receiver(post_save, sender=DeliveryAssignment)
def handle_completed_pickup(sender, instance, created, **kwargs):
    if (
        instance.assignment_type == DeliveryAssignment.AssignmentType.PICKUP
        and instance.status == DeliveryAssignment.Status.COMPLETED
    ):
        parcel = instance.parcel

        # Update parcel status
        if parcel.status != Parcel.Status.PICKED_UP:
            parcel.status = Parcel.Status.PICKED_UP
            parcel.save(update_fields=["status"])

            TrackingEvent.objects.create(
                parcel=parcel,
                event_type="PICKED_UP",
                location=parcel.pickup_location,
                updated_by=instance.agent.user,
                notes=f"Parcel collected by {instance.agent.agent_code}."
            )

        # Automatically create pickup commission
        commission_amount = instance.agent.pickup_commission_amount

        if commission_amount > 0:
            AgentCommission.objects.get_or_create(
                assignment=instance,
                defaults={
                    "agent": instance.agent,
                    "amount": commission_amount,
                    "status": AgentCommission.Status.PENDING,
                },
            )


@receiver(post_save, sender=DeliveryAssignment)
def handle_final_delivery_in_progress(sender, instance, created, **kwargs):
    if (
        instance.assignment_type == DeliveryAssignment.AssignmentType.DELIVERY
        and instance.status == DeliveryAssignment.Status.IN_PROGRESS
    ):
        parcel = instance.parcel

        if parcel.status != Parcel.Status.OUT_FOR_DELIVERY:
            parcel.status = Parcel.Status.OUT_FOR_DELIVERY
            parcel.save(update_fields=["status"])

            TrackingEvent.objects.create(
                parcel=parcel,
                event_type="OUT_FOR_DELIVERY",
                location=parcel.destination_location,
                updated_by=instance.agent.user,
                notes=(
                    f"Parcel is out for delivery with "
                    f"{instance.agent.agent_code}."
                )
            )


@receiver(post_save, sender=DeliveryAssignment)
def handle_completed_final_delivery(sender, instance, created, **kwargs):
    if (
        instance.assignment_type == DeliveryAssignment.AssignmentType.DELIVERY
        and instance.status == DeliveryAssignment.Status.COMPLETED
    ):
        parcel = instance.parcel

        # Update parcel status
        if parcel.status != Parcel.Status.DELIVERED:
            parcel.status = Parcel.Status.DELIVERED
            parcel.save(update_fields=["status"])

            TrackingEvent.objects.create(
                parcel=parcel,
                event_type="DELIVERED",
                location=parcel.destination_location,
                updated_by=instance.agent.user,
                notes=f"Parcel delivered by {instance.agent.agent_code}."
            )

        # Automatically create final-delivery commission
        commission_amount = instance.agent.delivery_commission_amount

        if commission_amount > 0:
            AgentCommission.objects.get_or_create(
                assignment=instance,
                defaults={
                    "agent": instance.agent,
                    "amount": commission_amount,
                    "status": AgentCommission.Status.PENDING,
                },
            )