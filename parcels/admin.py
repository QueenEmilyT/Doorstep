from django.contrib import admin

from .models import Parcel, TrackingSequence


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_number",
        "sender",
        "recipient_name",
        "pickup_location",
        "destination_location",
        "delivery_type",
        "delivery_fee",
        "status",
        "created_at",
    )

    search_fields = (
        "tracking_number",
        "recipient_name",
        "recipient_phone",
        "sender__username",
        "sender__email",
    )

    list_filter = (
        "delivery_type",
        "status",
        "pickup_location",
        "destination_location",
    )

    readonly_fields = (
        "tracking_number",
        "delivery_fee",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Parcel Information",
            {
                "fields": (
                    "tracking_number",
                    "sender",
                    "recipient_name",
                    "recipient_phone",
                    "recipient_email",
                )
            },
        ),
        (
            "Route Information",
            {
                "fields": (
                    "pickup_location",
                    "destination_location",
                    "transport_route",
                )
            },
        ),
        (
            "Package Information",
            {
                "fields": (
                    "description",
                    "weight_kg",
                    "declared_value",
                    "delivery_type",
                    "delivery_fee",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "special_instructions",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(TrackingSequence)
class TrackingSequenceAdmin(admin.ModelAdmin):
    list_display = (
        "year",
        "last_number",
    )