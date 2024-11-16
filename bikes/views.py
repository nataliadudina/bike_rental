from django_filters import rest_framework as filters
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from bikes.filters import BikeFilterSet
from bikes.models import Bicycle
from bikes.serializers import BikeSerializer
from users.permissions import IsModerator


class BikeViewSet(viewsets.ModelViewSet):
    """API эндпоинт для управления велосипедами"""

    serializer_class = BikeSerializer
    queryset = Bicycle.objects.all()

    def get_permissions(self):
        """Проверка прав доступа для изменения объекта велосипеда."""

        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = (IsAuthenticated, IsModerator)
        return super().get_permissions()


class AvailableBikesView(generics.ListAPIView):
    """API эндпоинт для получения списка доступных для аренды велосипедов"""

    serializer_class = BikeSerializer
    queryset = Bicycle.objects.filter(is_rented=False)
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = BikeFilterSet
