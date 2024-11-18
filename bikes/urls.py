from django.urls import include, path
from rest_framework.routers import DefaultRouter

from bikes.apps import BikesConfig
from bikes.views import AvailableBikesView, BikeViewSet

app_name = BikesConfig.name

router = DefaultRouter()
router.register(r"bicycles", BikeViewSet, basename="bicycles")

urlpatterns = [
    path("", include(router.urls)),
    path("available-bikes/", AvailableBikesView.as_view(), name="available-bikes"),
]
