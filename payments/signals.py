from django.db.models.signals import post_save
from django.dispatch import receiver

from parcels.models import Parcel

from .models import Payment


@receiver(post_save, sender=Parcel)
def create_payment_for_new_parcel(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.delivery_fee <= 0:
        return

    Payment.objects.get_or_create(
        parcel=instance,
        status=Payment.Status.PENDING,
        defaults={
            "amount": instance.delivery_fee,
        },
    )