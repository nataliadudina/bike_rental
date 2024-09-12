from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny

from users.permissions import IsOwner
from users.serializers import UserSerializer, UserProfileSerializer


class UserApiList(generics.ListAPIView):
    """ Представление для вывода списка пользователей """
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()


class UserRegistrationAPIView(generics.CreateAPIView):
    """ Представление для создания / регистрации пользователя """
    queryset = get_user_model().objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        password = self.request.data.get('password')
        if password:
            user.set_password(password)
            user.save()


class UserApiDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ Представление для чтения, обновления удаления записи о пользователе в бд """
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsOwner]

    def perform_update(self, serializer):
        user = serializer.save()
        password = self.request.data.get('password')
        if password:
            user.set_password(password)
            user.save()
