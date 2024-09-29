from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from bikes.models import Bicycle
from users.permissions import IsModerator
from bikes.serializers import BikeSerializer


class BikeViewSet(viewsets.ModelViewSet):
    """ API эндпоинт для управления велосипедами """

    serializer_class = BikeSerializer
    queryset = Bicycle.objects.all()

    def get_permissions(self):
        """ Проверка прав доступа для изменения объекта велосипеда. """

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = (IsAuthenticated, IsModerator)
        return super().get_permissions()


class AvailableBikesView(generics.ListAPIView):
    """ API эндпоинт для получения списка доступных велосипедов """

    serializer_class = BikeSerializer
    queryset = Bicycle.objects.filter(is_rented=False)
