from django.contrib.auth import get_user_model
from rest_framework import serializers

from rents.models import Rental
from users.models import Payment


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер пользователя"""

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = "__all__"


class BikeRentalHistorySerializer(serializers.ModelSerializer):
    """Сериалайзер истории аренды велосипедов. """

    class Meta:
        model = Rental()
        fields = ["id", "start_time", "end_time", "status", "rented_bike", "rental_cost"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['rented_bike'] = str(instance.rented_bike) if instance.rented_bike else None
        return representation


class PaymentSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра истории оплаты аренды велосипедов. """
    bike = serializers.CharField(source='rental.rented_bike')

    class Meta:
        model = Payment
        fields = ('id', 'bike', 'date', 'amount', 'method', 'status')
