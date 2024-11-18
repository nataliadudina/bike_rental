from rest_framework import serializers

from rents.models import Rental


class RentSerializer(serializers.ModelSerializer):
    renter = serializers.CharField(read_only=True)
    rented_bike = serializers.CharField(read_only=True)

    class Meta:
        model = Rental
        fields = "__all__"
