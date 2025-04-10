"""Define the serializers associated to the models."""

from rest_framework import serializers

from .models import Currency, CurrencyExchangeRate


class CurrencySerializer(serializers.HyperlinkedModelSerializer):
    """Define the serializer for Currency object model."""

    class Meta:
        """Set properties about the serializer and its behaviour."""

        model = Currency
        fields = "__all__"


class CurrencyExchangeRateSerializer(serializers.HyperlinkedModelSerializer):
    """Define the serializer for CurrencyExchangeRate object model."""

    class Meta:
        """Set properties about the serializer and its behaviour."""

        model = CurrencyExchangeRate
        fields = "__all__"
