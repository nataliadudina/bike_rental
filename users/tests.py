from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class UserTestCase(APITestCase):
    """
        Тестовый случай для проверки работы с моделью User.

        Этот класс содержит набор тестовых методов для проверки различных операций с пользователями,
        включая просмотр информации о пользователе, редактирование профиля и регистрацию новых пользователей.

        Атрибуты:
            client (APIClient): Клиент API для отправки HTTP-запросов.
            user (User): Существующий пользователь для тестирования.
            other_user (User): Другой существующий пользователь для сравнения.

        Методы:
            setUp(): Метод, вызываемый перед каждым тестовым методом. Инициализирует клиент API и создает пользователей.

        Примеры использования:
            # Проверка детального вида пользователя
            test_detail_view(self)
            # Проверка редактирования собственного профиля
            test_edit_own_profile(self)
            # Проверка редактирования чужого профиля
            test_edit_other_profile(self)

        Тесты в этом классе проверяют следующие сценарии:
        1. Просмотр информации о пользователе
        2. Редактирование собственного профиля
        3. Попытка редактирования чужого профиля
        4. Успешную регистрацию нового пользователя
        5. Попытку регистрации с дубликатом email
        6. Попытку регистрации без пароля
        """

    def setUp(self) -> None:
        # Создаем клиент API для отправки запросов
        self.client = APIClient()

        # Создаем пользователя для тестирования
        self.user = get_user_model().objects.create(email='user@example.com', password='password')

        # Генерируем токен доступа для пользователя
        access_token = str(RefreshToken.for_user(self.user).access_token)
        # Устанавливаем авторизацию для клиента
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Создаем второго пользователя для сравнения
        self.other_user = get_user_model().objects.create(email='other@example.com', password='other_password')

    def test_user_list_view(self):
        """ Тестирование просмотра списка пользователей. """
        # Создаем модератора
        self.moder = get_user_model().objects.create(email='moder@example.com', password='moder_password')
        moderator_group, _ = Group.objects.get_or_create(name='moderators')
        self.moder.groups.add(moderator_group)

        self.client.force_authenticate(user=self.moder)

        response = self.client.get(reverse('users:user-get'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка количества пользователей в ответе API
        self.assertEqual(len(response.data), 3)

        self.assertEqual(response.data[0]['email'], 'user@example.com')

    def test_user_detail_view(self):
        """ Тестирование просмотра пользователем информации о себе. """

        response = self.client.get(reverse('users:user-detail', kwargs={'pk': self.user.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['email'], self.user.email)
        self.assertTrue('first_name' in response.data)
        self.assertTrue('last_name' in response.data)

    def test_edit_own_profile(self):
        """ Тестирование редактирования своего профиля. """

        user_data = {
            'last_name': 'Dickens'
        }
        response = self.client.patch(reverse('users:user-detail', kwargs={'pk': self.user.pk}), data=user_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['last_name'], user_data['last_name'])

    def test_edit_other_profile(self):
        """ Тестирование прав доступа на редактирование чужого профиля. """

        user_data = {
            'last_name': 'Steinbeck'
        }
        access_token = str(RefreshToken.for_user(self.other_user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.patch(reverse('users:user-detail', kwargs={'pk': self.user.pk}), data=user_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserRegistrationTest(APITestCase):

    def test_successful_registration(self):
        """ Тест успешной регистрации пользователя. """

        new_user_data = {
            'email': 'user@example.com',
            'password': 'password',
            'first_name': 'New',
            'last_name': 'User'
        }

        url = reverse('users:user-register')
        response = self.client.post(url, new_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_user = get_user_model().objects.get(email=new_user_data['email'])
        self.assertTrue(new_user.check_password(new_user_data['password']))

        # Проверяем, что пароль хеширован
        self.assertTrue(new_user.check_password(new_user_data['password']))

    def test_duplicate_email(self):
        """ Тест попытки регистрации с уже существующим email. """

        # Создаем пользователя для тестирования
        self.user = get_user_model().objects.create(email='user@example.com', password='password')

        duplicate_user_data = {
            'email': self.user.email,
            'password': 'duplicatepassword123',
            'first_name': 'Duplicate',
            'last_name': 'User'
        }

        url = reverse('users:user-register')
        response = self.client.post(url, duplicate_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], 'user with this Email already exists.')

    def test_empty_password(self):
        """ Тест попытки регистрации без пароля. """

        empty_password_data = {
            'email': 'emptypassword@example.com',
            'first_name': 'Empty',
            'last_name': 'Password'
        }

        url = reverse('users:user-register')
        response = self.client.post(url, empty_password_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'][0], 'This field is required.')
