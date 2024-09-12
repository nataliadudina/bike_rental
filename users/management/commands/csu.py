import os

from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    """
       Custom management command to create a superuser.
       python manage.py csu

       This command creates a superuser account using environment variables for the email
       and password. It is intended to be used in environments where interactive superuser
       creation is not possible, such as during deployments or in Docker containers.

       The environment variables SUPERUSER_EMAIL and SUPERUSER_PASSWORD should be set
       before running this command. If these variables are not set, the command will fail
       to create a superuser.
       """
    help = 'Create a superuser'

    def handle(self, *args, **options):
        user = User.objects.create(
            email=os.getenv('SUPERUSER_EMAIL'),
            is_superuser=True,
            is_staff=True,
            is_active=True
        )

        user.set_password(os.getenv('SUPERUSER_PASSWORD'))
        user.save()
