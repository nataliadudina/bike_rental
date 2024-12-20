import logging
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bikes.models import Bicycle
from rents.models import Rental
from rents.serializers import RentSerializer
from rents.tasks import get_rental_cost
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
                logging.warning(f"{bike} with bike id {bike_id} is already rented.")
                raise serializers.ValidationError("Bicycle is not available.")

            # Проверка, нет ли у пользователя активной аренды
            active_rentals = Rental.objects.filter(renter=self.request.user).filter(
                status="active"
            )
            if active_rentals.exists():
                logging.warning(f"{self.request.user} has an active rental.")
                raise serializers.ValidationError("User already has an active rental.")

            serializer.save(rented_bike=bike, renter=self.request.user, status="active")

            # Изменение статуса велосипеда
            bike.is_rented = True
            bike.save()

            # Логирование начала аренды
            logging.info(f"{self.request.user} started rental {bike} with bike id {bike_id}.")

        except ObjectDoesNotExist:
            logging.warning(f"Bicycle with id {bike_id} not found.")
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

    def get_object(self, queryset=None):
        rental_id = self.kwargs.get('pk')
        return get_object_or_404(Rental, pk=rental_id)

    def retrieve(self, request, *args, **kwargs):
        """ Просмотр записи об аренде доступен только арендатору, модератору и суперпользователю."""

        rental = self.get_object()
        if rental.renter == request.user or request.user.is_staff or request.user.is_superuser:
            result = super().retrieve(request, *args, **kwargs)
        else:
            return Response({"detail": "You do not have permission to view this rental"}, status=403)
        return result


class ReturnView(generics.UpdateAPIView):
    """API эндпоинт для обновления записи об аренде велосипеда - возврат велосипеда."""

    queryset = Rental.objects.all()
    serializer_class = RentSerializer
    permission_classes = (IsAuthenticated,)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()  # Получаем запись об аренде из бд

        # Только пользователь, арендовавший велосипед, может его вернуть
        if instance.renter != request.user:
            logging.warning(f"{instance.renter} is not authorized to complete rental # {instance.pk}")
            return Response(
                {"error": "Not authorized to return this bike."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Проверка, что аренда ещё активна
        if instance.status != "active":
            logging.warning(f"Rental {instance.pk} is already completed.")
            return Response(
                {"error": "Rental is already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Обновление статуса аренды
        instance.status = "pending"
        instance.end_time = now()
        instance.save()

        logging.info(f"Rental {instance.pk} is completed and payment is pending.")

        # Фоновая задача расчёта платы за аренду
        payment_task = get_rental_cost.delay(instance.pk)
        payment_task.get()

        result = payment_task.result

        if result and result.get('status') == 'success':
            rental_cost = Decimal(result['rental_cost'])
            instance.rental_cost = rental_cost
            instance.save()

            logging.info(f"Payment for rental {instance.pk} is successfully calculated.")
        else:
            raise ValueError(f"Ошибка при расчете стоимости аренды: {result}")

        # Изменение статуса велосипеда
        bike_id = instance.rented_bike.id  # Получаем ID велосипеда
        bike = Bicycle.objects.get(id=bike_id)
        bike.is_rented = False
        bike.save()
        return Response(
            self.serializer_class(instance).data, status=status.HTTP_200_OK
        )
