from django.contrib import admin

from .models import TrackingEvent


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = (
        "parcel",
        "event_type",
        "location",
        "updated_by",
        "event_time",
    )

    search_fields = (
        "parcel__tracking_number",
        "updated_by__username",
        "notes",
    )

    list_filter = (
        "event_type",
        "location",
        "event_time",
    )

    readonly_fields = (
        "event_time",
        "created_at",
    )