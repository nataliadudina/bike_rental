# Generated by Django 5.0.7 on 2024-10-17 09:43

import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rents", "0004_alter_rental_rental_cost"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Payment date"
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=10,
                        null=True,
                        verbose_name="Payment amount",
                    ),
                ),
                (
                    "method",
                    models.CharField(
                        choices=[("cash", "Cash"), ("transfer", "Bank transfer")],
                        max_length=10,
                        verbose_name="Payment method",
                    ),
                ),
                ("session_id", models.CharField(blank=True, max_length=100, null=True)),
                ("status", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "payment_link",
                    models.URLField(
                        blank=True,
                        max_length=400,
                        null=True,
                        verbose_name="Payment link",
                    ),
                ),
                (
                    "stripe_product_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "rental",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="rents.rental",
                        verbose_name="Rental payment",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Payment",
                "verbose_name_plural": "Payments",
            },
        ),
    ]
