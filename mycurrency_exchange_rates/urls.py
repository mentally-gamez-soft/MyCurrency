"""Declare the listing of the urls."""

from django.urls import include, path
from rest_framework import routers

from .views import CurrencyExchangeRateViewSet, CurrencyViewSet

router = routers.DefaultRouter()
router.register("currency", CurrencyViewSet)
router.register("currency-converter", CurrencyExchangeRateViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
