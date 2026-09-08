from django.contrib import admin

from .models import Payment, AgentCommission


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "parcel",
        "amount",
        "payment_timing",
        "payment_method",
        "status",
        "transaction_reference",
        "paid_at",
    )

    search_fields = (
        "parcel__tracking_number",
        "transaction_reference",
    )

    list_filter = (
        "payment_timing",
        "payment_method",
        "status",
        "paid_at",
    )

    readonly_fields = (
        "paid_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Payment Information",
            {
                "fields": (
                    "parcel",
                    "amount",
                    "payment_timing",
                    "payment_method",
                    "status",
                    "transaction_reference",
                )
            },
        ),
        (
            "Automatic Timestamp",
            {
                "fields": (
                    "paid_at",
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


@admin.register(AgentCommission)
class AgentCommissionAdmin(admin.ModelAdmin):
    list_display = (
        "agent",
        "assignment",
        "amount",
        "status",
        "approved_at",
        "paid_at",
    )

    search_fields = (
        "agent__agent_code",
        "assignment__parcel__tracking_number",
        "payment_reference",
    )

    list_filter = (
        "status",
        "approved_at",
        "paid_at",
    )

    readonly_fields = (
        "approved_at",
        "paid_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Commission Information",
            {
                "fields": (
                    "agent",
                    "assignment",
                    "amount",
                    "status",
                    "payment_reference",
                )
            },
        ),
        (
            "Automatic Timestamps",
            {
                "fields": (
                    "approved_at",
                    "paid_at",
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