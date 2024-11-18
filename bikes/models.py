from django.db import models


class Bicycle(models.Model):
    """Класс для таблицы 'Велосипед'"""

    TYPE_CHOICES = [
        ("A", "Adult"),
        ("J", "Junior"),
        ("K", "Kids"),
    ]

    CONDITION_CHOICES = [
        ("E", "Excellent"),
        ("G", "Good"),
        ("S", "Satisfactory"),
    ]

    FRAME_TYPE_CHOICES = [
        ("U", "Urban"),
        ("M", "Mountain"),
        ("R", "Road"),
        ("T", "Touring"),
    ]

    brand = models.CharField(max_length=50)
    condition = models.CharField(max_length=12, choices=CONDITION_CHOICES)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    gear_count = models.IntegerField()
    frame_type = models.CharField(max_length=8, choices=FRAME_TYPE_CHOICES)
    wheel_size = models.IntegerField()
    colour = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(upload_to="bicycles/", null=True, blank=True)
    rental_cost_hour = models.DecimalField(max_digits=5, decimal_places=2)
    rental_cost_day = models.DecimalField(max_digits=5, decimal_places=2)
    is_rented = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.brand} - {self.get_type_display()} - {self.get_frame_type_display()}"

    class Meta:
        verbose_name = "bicycle"
        verbose_name_plural = "bicycles"
