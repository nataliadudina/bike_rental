from django.db import models

from bikes.models import Bicycle
from config.settings import AUTH_USER_MODEL


class Rental(models.Model):
    """Класс для таблицы 'Аренда'"""

    RENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("completed", "Completed"),
    ]

    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    rented_bike = models.ForeignKey(
        Bicycle, null=True, on_delete=models.SET_NULL, related_name="rentals"
    )
    renter = models.ForeignKey(
        AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="rents"
    )
    status = models.CharField(
        max_length=9, choices=RENT_STATUS_CHOICES, default="pending"
    )
    rental_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=0
    )

    def __str__(self):
        return f"{self.rented_bike} - {self.renter} - {self.status}"

    class Meta:
        verbose_name = "rental"
        verbose_name_plural = "rentals"
