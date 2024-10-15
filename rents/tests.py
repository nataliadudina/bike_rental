from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from bikes.models import Bicycle
from rents.models import Rental
from users.models import User


class RentTestcase(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Создаем несколько велосипедов
        self.bike1 = baker.make(Bicycle)
        self.bike2 = baker.make(Bicycle, is_rented=True)

        # Создаем пользователей
        self.user1 = baker.make(User)
        self.client.force_authenticate(user=self.user1)
        self.user2 = baker.make(User)
        self.client.force_authenticate(user=self.user2)

    def test_rent_bike(self):
        """Тестирование создания записи об аренде велосипеда."""

        data = {
            "renter": self.user1.pk
        }

        response = self.client.post(reverse("rents:rent-bike", kwargs={"bike_id": self.bike1.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("renter", response.data)

        # Проверяем, что была создана новая запись в модели Rent
        self.assertEqual(Rental.objects.count(), 1)
        rent = Rental.objects.first()
        self.assertEqual(rent.rented_bike, self.bike1)

        # Дополнительная проверка
        bike_from_db = Bicycle.objects.get(pk=self.bike1.pk)
        self.assertTrue(bike_from_db.is_rented)

    def test_rent_unavailable_bike(self):
        """Тестирование попытки аренды недоступного велосипеда."""

        data = {
            "renter": self.user1.pk
        }
        response = self.client.post(reverse("rents:rent-bike", kwargs={"bike_id": self.bike2.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for item in response.data[1:]:
            self.assertIn('detail', item)
            self.assertIn('code', item)
            self.assertEqual(item["error_detail"], "Bicycle is not available.")
            self.assertEqual(item['code'], 'invalid')

    def test_rent_nonexistent_bike(self):
        """Тестирование попытки аренды несуществующего велосипеда."""

        data = {
            "renter": self.user1.pk
        }
        response = self.client.post(reverse("rents:rent-bike", kwargs={"bike_id": 15}), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for item in response.data[1:]:
            self.assertIn('detail', item)
            self.assertIn('code', item)
            self.assertEqual(item["error_detail"], "Bicycle not found.")
            self.assertEqual(item['code'], 'invalid')

    def test_rent_second_bike(self):
        """Тестирование попытки аренды второго велосипеда."""
        self.rental1 = baker.make(Rental, rented_bike=self.bike2, renter=self.user2, status="active")

        data = {
            "renter": self.user2.pk
        }
        response = self.client.post(reverse("rents:rent-bike", kwargs={"bike_id": self.bike1.pk}), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for item in response.data[1:]:
            self.assertIn('detail', item)
            self.assertIn('code', item)
            self.assertEqual(item["error_detail"], "User already has an active rental.")
            self.assertEqual(item['code'], 'invalid')


class TestRentApiViews(APITestCase):
    """ Тестовые случаи для API-представлений аренд."""

    def setUp(self):
        self.user = baker.make(User)
        self.client.force_authenticate(user=self.user)

        # Создаем модератора
        self.moder = get_user_model().objects.create(
            email="moder@example.com", password="moder_password"
        )
        moderator_group, _ = Group.objects.get_or_create(name="moderators")
        self.moder.groups.add(moderator_group)

        self.bike = baker.make(Bicycle)
        self.rental = Rental.objects.create(rented_bike=self.bike, renter=self.user, start_time=now())

        self.list_url = reverse('rents:rent-list')
        self.retrieve_url = reverse('rents:rent-read', args=[self.rental.pk])

    def test_list_view(self):
        """ Тест просмотра списка аренд."""

        self.client.force_authenticate(user=self.moder)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['rented_bike'], str(self.bike))
        self.assertEqual(response.data[0]['renter'], str(self.user))

    def test_retrieve_view(self):
        """ Тест получения информации о конкретной аренде."""

        self.client.force_authenticate(user=self.moder)
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rented_bike'], str(self.bike))
        self.assertEqual(response.data['renter'], str(self.user))

    def test_unauthenticated_access(self):
        """ Тест доступа без аутентификации к списку аренд."""

        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_access(self):
        """ Тест попытки доступа неавторизованного пользователя к списку аренд."""

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('rents:rent-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestReturnView(APITestCase):
    """ Тестовые случаи для API-представлений возврата велосипедов."""

    def setUp(self):
        self.user1 = baker.make(User)
        self.client.force_authenticate(user=self.user1)

        self.user2 = baker.make(User)
        self.client.force_authenticate(user=self.user2)

        self.bike = baker.make(Bicycle)

        self.rental = Rental.objects.create(
            rented_bike=self.bike,
            renter=self.user1,
            start_time=now() - timedelta(hours=2),
            status="active",
        )

    def test_return_bike(self):
        """ Тест успешного возврата велосипеда."""

        # Пользователь пытается вернуть свой велосипед
        url = reverse('rents:return-bike', kwargs={'pk': self.rental.pk})
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(url, {'status': 'completed'})

        # Проверяем, что аренда завершилась
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

        # Проверяем, что велосипед стал доступным
        available_bike = Bicycle.objects.get(pk=self.bike.pk)
        self.assertFalse(available_bike.is_rented)

    def test_not_authorized_to_return(self):
        """ Тест попытки возврата велосипеда пользователем без прав."""

        self.client.force_authenticate(user=self.user2)
        url = reverse('rents:return-bike', kwargs={'pk': self.rental.pk})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rental_already_completed(self):
        """ Тест попытки возврата аренды, которая уже завершена."""

        self.client.force_authenticate(user=self.user1)
        self.rental.status = "completed"
        self.rental.save()
        url = reverse('rents:return-bike', kwargs={'pk': self.rental.pk})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rental_not_found(self):
        """ Тест попытки возврата несуществующей аренды."""

        url = reverse('rents:return-bike', kwargs={'pk': 9999})
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_bike_not_found(self):
        """ Тест попытки возврата аренды без велосипеда."""

        self.rental.rented_bike = None
        self.rental.save()
        url = reverse('rents:return-bike', kwargs={'pk': self.rental.pk})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
