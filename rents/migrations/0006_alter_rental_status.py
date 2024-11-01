# Generated by Django 5.0.7 on 2024-10-18 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rents", "0005_alter_rental_rental_cost"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rental",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("active", "Active"),
                    ("completed", "Completed"),
                ],
                default="pending",
                max_length=9,
            ),
        ),
    ]