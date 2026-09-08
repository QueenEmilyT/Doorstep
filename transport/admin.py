from django.contrib import admin

from .models import (
    Location,
    TransportCompany,
    TransportRoute,
    TransportHandover,
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "town",
        "district",
        "is_active",
        "created_at",
    )

    search_fields = (
        "town",
        "district",
    )

    list_filter = (
        "district",
        "is_active",
    )


@admin.register(TransportCompany)
class TransportCompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "contact_person",
        "phone",
        "email",
        "is_active",
    )

    search_fields = (
        "name",
        "contact_person",
        "phone",
        "email",
    )

    list_filter = (
        "is_active",
    )


@admin.register(TransportRoute)
class TransportRouteAdmin(admin.ModelAdmin):
    list_display = (
        "transport_company",
        "origin",
        "destination",
        "normal_delivery_fee",
        "express_delivery_fee",
        "is_active",
    )

    search_fields = (
        "transport_company__name",
        "origin__town",
        "destination__town",
    )

    list_filter = (
        "transport_company",
        "is_active",
    )


@admin.register(TransportHandover)
class TransportHandoverAdmin(admin.ModelAdmin):
    list_display = (
        "parcel",
        "transport_route",
        "status",
        "received_at_origin_at",
        "dispatched_at",
        "arrived_at_destination_at",
        "updated_at",
    )

    search_fields = (
        "parcel__tracking_number",
        "transport_route__transport_company__name",
    )

    list_filter = (
        "status",
        "transport_route__transport_company",
    )

    readonly_fields = (
        "received_at_origin_at",
        "dispatched_at",
        "arrived_at_destination_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Transport Handover",
            {
                "fields": (
                    "parcel",
                    "transport_route",
                    "status",
                    "notes",
                )
            },
        ),
        (
            "Automatic Timestamps",
            {
                "fields": (
                    "received_at_origin_at",
                    "dispatched_at",
                    "arrived_at_destination_at",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )