from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """ Сериалайзер профиля пользователя """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    """ Просмотр профиля пользователя """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = '__all__'
