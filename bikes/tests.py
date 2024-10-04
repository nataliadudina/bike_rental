from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from bikes.models import Bicycle
from users.models import User


class BikeTestCase(TestCase):
    """
    Тестовый класс для BikeViewSet.

    Этот класс содержит набор тестовых случаев для BikeViewSet,
    включая тесты на создание, чтение, обновление и удаление велосипедов.
    """

    def setUp(self):
        """
        Метод для подготовки тестовой среды.

        Создает клиент API, пользователя-модератора и несколько велосипедов для использования в тестах.
        """
        self.client = APIClient()

        # Создаем модератора, т.к. он может управлять данными
        self.moder = baker.make(User, is_staff=True)
        moderator_group, _ = Group.objects.get_or_create(name="moderators")
        self.moder.groups.add(moderator_group)
        self.client.force_authenticate(user=self.moder)

        # Создаем несколько велосипедов
        self.bike1 = baker.make(Bicycle)
        self.bike2 = baker.make(Bicycle)
        self.bike3 = baker.make(Bicycle, rented=True)

    def test_create_bike(self):
        """Тестирование создания велосипеда."""

        data = {
            "brand": "Test Brand",
            "condition": "G",
            "type": "J",
            "gear_count": 6,
            "frame_type": "M",
            "wheel_size": 26,
            "rental_cost_hour": 10.00,
            "rental_cost_day": 52.00,
        }
        response = self.client.post(reverse("bikes:bicycles-list"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)

    def test_retrieve_bike(self):
        """Тестирование чтения одной записи."""

        response = self.client.get(
            reverse("bikes:bicycles-detail", kwargs={"pk": self.bike1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_bike(self):
        """Тестирование изменения записи."""

        new_data = {"brand": "Better Brand"}
        response = self.client.patch(
            reverse("bikes:bicycles-detail", kwargs={"pk": self.bike1.pk}), new_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["brand"], "Better Brand")

    def test_destroy_bike(self):
        """Тестирование удаления записи."""

        response = self.client.delete(
            reverse("bikes:bicycles-detail", kwargs={"pk": self.bike1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_bikes(self):
        """Тестирование чтения списка записей."""

        response = self.client.get(reverse("bikes:bicycles-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_available_bikes(self):
        """Тестирование чтения списка доступных велосипедов."""

        response = self.client.get(reverse("bikes:available-bikes"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Только неарендованный велосипед


class BikePermsTestCase(TestCase):
    """
    Тестовый класс для проверки разрешений пользователей BikeViewSet.

    Этот класс содержит тесты для проверки прав доступа пользователей к операциям
    создания, обновления и удаления велосипедов в BikeViewSet.
    """

    def setUp(self):
        """
        Метод для подготовки тестовой среды.

        Создает клиент API, обычного пользователя и несколько велосипедов для использования в тестах.
        """

        self.client = APIClient()
        self.user = baker.make(User)
        self.client.force_authenticate(user=self.user)

        # Создаем несколько велосипедов
        self.bike1 = baker.make(Bicycle)
        self.bike2 = baker.make(Bicycle)

    def test_create_nonmoderator(self):
        """Тестирование запрета на создание записей немодераторами."""

        response = self.client.post(reverse("bikes:bicycles-list"), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonmoderator(self):
        """Тестирование запрета на изменение записи немодераторами."""

        response = self.client.put(
            reverse("bikes:bicycles-detail", kwargs={"pk": self.bike1.pk}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonmoderator(self):
        """Тестирование запрета на удаление записи немодераторами."""

        response = self.client.delete(
            reverse("bikes:bicycles-detail", kwargs={"pk": self.bike1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
