import logging

from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bikes.models import Bicycle
from rents.models import Rental
from rents.serializers import RentSerializer
from rents.utils import calculate_rental_cost
from users.permissions import IsModerator

logger = logging.getLogger(__name__)


class RentApiView(generics.CreateAPIView):
    """API эндпоинт для создания записей об аренде велосипеда."""

    serializer_class = RentSerializer
    queryset = Rental.objects.all()
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        bike_id = self.kwargs.get("bike_id")  # Получаем ID велосипеда из URL

        try:
            bike = Bicycle.objects.get(id=bike_id)
            # Проверка, доступен ли велосипед для аренды
            if bike.is_rented:
                raise serializers.ValidationError("Bicycle is not available.")

            # Проверка, нет ли у пользователя активной аренды
            active_rentals = Rental.objects.filter(renter=self.request.user).filter(
                status="active"
            )
            if active_rentals.exists():
                raise serializers.ValidationError("User already has an active rental.")

            serializer.save(rented_bike=bike, renter=self.request.user, status="active")

            # Изменение статуса велосипеда
            bike.is_rented = True
            bike.save()

        except ObjectDoesNotExist:
            raise serializers.ValidationError("Bicycle not found.")


class RentListApiView(generics.ListAPIView):
    """API эндпоинт для просмотра всех записей об аренде велосипеда."""

    serializer_class = RentSerializer
    queryset = Rental.objects.all()
    permission_classes = (IsAuthenticated, IsModerator)


class RentRetrieveApiView(generics.RetrieveAPIView):
    """API эндпоинт для просмотра одной записи об аренде велосипеда."""

    serializer_class = RentSerializer
    queryset = Rental.objects.all()
    permission_classes = (IsAuthenticated, IsModerator)


class ReturnView(generics.UpdateAPIView):
    """API эндпоинт для обновления записи об аренде велосипеда - возврат велосипеда."""

    queryset = Rental.objects.all()
    serializer_class = RentSerializer
    permission_classes = (IsAuthenticated,)

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()  # Получаем запись об аренде из бд

            # Проверяем наличие велосипеда в аренде
            if not instance.rented_bike:
                return Response(
                    {"detail": "Bike not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Только пользователь, арендовавший велосипед, может его вернуть
            if instance.renter != request.user:
                return Response(
                    {"error": "Not authorized to return this bike."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Проверка, что аренда ещё не завершена
            if instance.status == "completed":
                return Response(
                    {"error": "Rental is already completed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Обновление статуса аренды
            instance.status = "completed"
            instance.end_time = now()
            instance.rental_cost = calculate_rental_cost(instance)
            instance.save()

            # Изменение статуса велосипеда
            bike_id = instance.rented_bike.id  # Получаем ID велосипеда
            bike = Bicycle.objects.get(id=bike_id)
            bike.is_rented = False
            bike.save()

            logger.info(
                f"Successful bike return: Rental ID={instance.id}, Bike ID={bike_id}"
            )

            return Response(
                self.serializer_class(instance).data, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error during bike return: {str(e)}")
            return Response(
                {"error": "An error occurred during bike return"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
