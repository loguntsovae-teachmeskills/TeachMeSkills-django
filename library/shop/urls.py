from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CheckoutViewSet


urlpatterns = [
    path("checkout/", CheckoutViewSet.as_view(), name="checkout"),
]
