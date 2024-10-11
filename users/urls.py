from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from users.apps import UsersConfig
from users.views import UserApiDetailView, UserApiList, UserRentHistory, UserRegistrationAPIView

app_name = UsersConfig.name

urlpatterns = [
    path("users/", UserApiList.as_view(), name="user-get"),
    path("users/<int:pk>/", UserApiDetailView.as_view(), name="user-detail"),
    path("history/", UserRentHistory.as_view(), name="user-history"),
    # регистрация пользователя
    path("register/", UserRegistrationAPIView.as_view(), name="user-register"),
    # авторизация пользователей
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="token_obtain_pair",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
