from rest_framework import serializers

from bikes.models import Bicycle


class BikeSerializer(serializers.ModelSerializer):
    """Сериалайзер велосипеда"""

    class Meta:
        model = Bicycle
        fields = "__all__"
