from django.contrib import admin

from .models import DeliveryAssignment


@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "parcel",
        "agent",
        "assignment_type",
        "status",
        "assigned_at",
        "accepted_at",
        "started_at",
        "completed_at",
    )

    search_fields = (
        "parcel__tracking_number",
        "agent__agent_code",
        "agent__user__username",
    )

    list_filter = (
        "assignment_type",
        "status",
        "assigned_at",
    )

    readonly_fields = (
        "assigned_at",
        "accepted_at",
        "started_at",
        "completed_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Assignment Information",
            {
                "fields": (
                    "parcel",
                    "agent",
                    "assignment_type",
                    "status",
                    "notes",
                )
            },
        ),
        (
            "Automatic Timestamps",
            {
                "fields": (
                    "assigned_at",
                    "accepted_at",
                    "started_at",
                    "completed_at",
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