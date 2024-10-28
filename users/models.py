from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models

from rents.models import Rental


class User(AbstractUser):
    """Кастомная модель пользователя, расширяющая абстрактный класс пользователя."""

    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=50, verbose_name="First Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Payment date')
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, null=True, blank=True, related_name='payments',
                               verbose_name='Rental payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), null=True, blank=True,
                                 verbose_name='Payment amount')

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Bank transfer'),
    ]
    method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, verbose_name='Payment method')
    session_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    payment_link = models.URLField(max_length=400, blank=True, null=True, verbose_name='Payment link')
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.rental} - {self.date} - {self.amount}"

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ["-date"]
