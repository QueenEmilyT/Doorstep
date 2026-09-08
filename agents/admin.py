from django.contrib import admin

from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = (
        "agent_code",
        "user",
        "district",
        "town",
        "verification_status",
        "is_available",
        "pickup_commission_amount",
        "delivery_commission_amount",
        "joined_at",
    )

    search_fields = (
        "agent_code",
        "user__username",
        "user__email",
        "user__phone",
        "district",
        "town",
        "national_id_number",
    )

    list_filter = (
        "verification_status",
        "is_available",
        "district",
    )

    readonly_fields = (
        "joined_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Agent Information",
            {
                "fields": (
                    "user",
                    "agent_code",
                    "district",
                    "town",
                    "address",
                    "national_id_number",
                )
            },
        ),
        (
            "Verification & Availability",
            {
                "fields": (
                    "verification_status",
                    "is_available",
                )
            },
        ),
        (
            "Commission Settings",
            {
                "fields": (
                    "pickup_commission_amount",
                    "delivery_commission_amount",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "joined_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    ordering = (
        "-joined_at",
    )