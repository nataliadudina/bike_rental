# Generated by Django 5.0.7 on 2024-09-29 21:09

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bikes", "0002_rename_rented_bicycle_is_rented"),
        ("rents", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Rent",
            new_name="Rental",
        ),
        migrations.AlterModelOptions(
            name="rental",
            options={"verbose_name": "rental", "verbose_name_plural": "rentals"},
        ),
    ]
