from django.contrib import admin

from rents.models import Rental


@admin.register(Rental)
class UserAdmin(admin.ModelAdmin):
    """Админ-панель для управления арендой велосипедов."""

    list_display = (
        "pk",
        "start_time",
        "end_time",
        "rented_bike",
        "renter",
        "status",
        "rental_cost",
    )
    list_display_links = ("pk", "start_time")
    ordering = ("start_time", "end_time")
    list_editable = ("status",)
    readonly_fields = (
        "rented_bike",
        "renter",
    )
    list_filter = ("rented_bike",)
    list_per_page = 10
