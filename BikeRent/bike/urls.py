from django.urls import path

from .views import BikeDetailView, BikeView, StationView

urlpatterns = [
    path("bikes/<int:pk>/", BikeDetailView.as_view(), name="bike-view"),
    path("bikes/", BikeView.as_view(), name="bike-list"),
    path("stations/", StationView.as_view(), name="station-list"),
]
