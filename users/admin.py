from django.contrib import admin

from .models import User, CustomerProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "phone",
        "role",
        "account_status",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "phone",
        "first_name",
        "last_name",
    )

    list_filter = (
        "role",
        "account_status",
        "is_staff",
        "is_active",
        "is_phone_verified",
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone_number",
        "district",
        "address",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__phone",
        "district",
        "address",
    )

    list_filter = (
        "district",
        "created_at",
    )

    @admin.display(description="Phone Number")
    def phone_number(self, obj):
        return obj.user.phone