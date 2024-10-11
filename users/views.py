from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bikes.models import Bicycle
from rents.models import Rental
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator
from users.serializers import UserSerializer, BikeRentalHistorySerializer


class UserApiList(generics.ListAPIView):
    """Представление для вывода списка пользователей."""

    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated, IsModerator]


class UserRegistrationAPIView(generics.CreateAPIView):
    """Представление для создания / регистрации пользователя."""

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        password = self.request.data.get("password")
        if password:
            user.set_password(password)
            user.save()


class UserApiDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Представление для чтения, обновления удаления записи о пользователе в бд."""

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def perform_update(self, serializer):
        user = serializer.save()
        password = self.request.data.get("password")
        if password:
            user.set_password(password)
            user.save()

    def get_permissions(self):
        """Проверка прав доступа для изменения профиля."""

        # Определяем права доступа на основе метода запроса
        if self.request.method == "GET":
            permission_classes = (IsAuthenticated, IsOwnerOrModerator)
        elif self.request.method in ["PUT", "PATCH", "DELETE"]:
            permission_classes = (IsAuthenticated, IsOwner)
        self.permission_classes = permission_classes
        return super().get_permissions()


class UserRentHistory(APIView):
    """ Представление для просмотра истории аренды велосипедов пользователя."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        history = Rental.objects.filter(renter=user)
        serializer = BikeRentalHistorySerializer(history, many=True)
        return Response(serializer.data)
