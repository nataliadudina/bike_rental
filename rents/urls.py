from django.urls import path

from rents.apps import RentsConfig
from rents.views import (RentApiView, RentListApiView, RentRetrieveApiView,
                         ReturnView)

app_name = RentsConfig.name

urlpatterns = [
    path("rent/<int:bike_id>/", RentApiView.as_view(), name="rent-bike"),
    path("rentals/", RentListApiView.as_view(), name="rent-list"),
    path("rentals/<int:pk>/", RentRetrieveApiView.as_view(), name="rent-read"),
    path("returns/<int:pk>/", ReturnView.as_view(), name="return-bike"),
]
