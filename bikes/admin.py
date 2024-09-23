from django.contrib import admin

from bikes.models import Bicycle


@admin.register(Bicycle)
class BikeAdmin(admin.ModelAdmin):
    """ Админ-панель для управления велосипедами. """

    fields = ('brand', 'condition', 'type', 'gear_count', 'frame_type', 'wheel_size', 'colour', 'image',
              'rental_cost_hour', 'rental_cost_day', 'rented')
    list_display = ('pk', 'brand', 'condition', 'type', 'rented')
    list_display_links = ('brand',)
    search_fields = ('brand', 'condition')
    list_filter = ('rented', 'type', 'condition')
    ordering = ('rental_cost_hour',)
    list_editable = ('rented',)
    list_per_page = 10
