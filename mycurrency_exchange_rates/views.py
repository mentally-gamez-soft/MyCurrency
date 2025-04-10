"""Declare the views and endpoints."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Currency, CurrencyExchangeRate
from .serializers import CurrencyExchangeRateSerializer, CurrencySerializer


class CurrencyExchangeRateViewSet(viewsets.ModelViewSet):
    """Define API endpoint to get the value exchange for a currency."""

    queryset = CurrencyExchangeRate.objects.all()
    serializer_class = CurrencyExchangeRateSerializer

    def list(self, request, *args, **kwargs):
        """Get all the CurrencyExchangeRates."""
        # 1. check in cache

        # 2. check in DB

        # 3. call API

        print("args => {}".format(args))
        print("kwargs => {}".format(kwargs))
        print(request)
        print(request.query_params.keys())
        print(type(request.query_params))

        if "from_currency" not in request.query_params.keys():
            return Response(
                [
                    {
                        "status": "ko",
                        "message": (
                            "The currency code source must be specified !"
                        ),
                    }
                ]
            )
        if "to_currency" not in request.query_params.keys():
            print(" **************   TEST HERE ***************")
            return Response(
                [
                    {
                        "status": "ko",
                        "mesage": (
                            "The currency code destination must be specified !"
                        ),
                    }
                ]
            )

        from_currency = request.query_params.get("from_currency")
        to_currency = request.query_params.get("to_currency")

        queryset = CurrencyExchangeRate.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        print(type(serializer.data))
        print(serializer.data)
        return Response(serializer.data)


class CurrencyViewSet(viewsets.ModelViewSet):
    """Define API endpoint to get the currency."""

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    def list(self, request, *args, **kwargs):
        """Get all the Currencies."""
        print("overriding here.")
        queryset = Currency.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        print(type(serializer.data))
        print(serializer.data)
        return Response(serializer.data)
