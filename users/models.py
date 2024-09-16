from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Кастомная модель пользователя, расширяющая абстрактный класс пользователя. """

    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=50, verbose_name='First Name')
    last_name = models.CharField(max_length=50, verbose_name='Last Name')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.email}'
