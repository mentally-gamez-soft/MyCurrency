"""Declare the views and endpoints."""

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.response import Response

from mycurrency_exchange_rates.services.database_managers.managers import (
    get_conversion_from_database,
)
from mycurrency_exchange_rates.tools import validate_arrow_date

from .models import Currency, CurrencyExchangeRate
from .serializers import CurrencyExchangeRateSerializer, CurrencySerializer


class CurrencyExchangeRateViewSet(viewsets.ModelViewSet):
    """Define API endpoint to get the value exchange for a currency."""

    queryset = CurrencyExchangeRate.objects.all()
    serializer_class = CurrencyExchangeRateSerializer

    def __is_valid_query(
        self, from_currency, to_currency, valuation_date
    ) -> dict:
        if not from_currency:
            return {
                "status": "ko",
                "message": "The currency code source must be specified !",
            }
        if not to_currency:
            return {
                "status": "ko",
                "mesage": "The currency code destination must be specified !",
            }

        if not valuation_date:
            return {
                "status": "ko",
                "mesage": "The valuation date must be specified !",
            }
        try:
            valuation_year = int(valuation_date.split("-")[0])
        except:
            return {
                "status": "ko",
                "mesage": "The valuation date is incorrect !",
            }
        try:
            valuation_month = int(valuation_date.split("-")[1])
        except:
            return {
                "status": "ko",
                "mesage": "The valuation date is incorrect !",
            }
        try:
            valuation_day = int(valuation_date.split("-")[2])
        except:
            return {
                "status": "ko",
                "mesage": "The valuation date is incorrect !",
            }

        return {
            "status": "ok",
            "valuation_year": valuation_year,
            "valuation_month": valuation_month,
            "valuation_day": valuation_day,
        }

    @method_decorator(cache_page(60 * 30, key_prefix="c-exchange_rates-"))
    def list(self, request, *args, **kwargs):
        """Get all the CurrencyExchangeRates."""
        from_currency = request.query_params.get("from_currency", None)
        to_currency = request.query_params.get("to_currency", None)
        valuation_date = request.query_params.get("valuation_date", None)

        valid_params = self.__is_valid_query(
            from_currency, to_currency, valuation_date
        )
        if "ko" in valid_params["status"]:
            return Response([valid_params])

        arrow_date = validate_arrow_date(
            valid_params["valuation_year"],
            valid_params["valuation_month"],
            valid_params["valuation_day"],
        )

        if "ko" in arrow_date["status"]:
            return Response([arrow_date])

        return Response(
            [
                get_conversion_from_database(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    valuation_date=arrow_date["arrow_date"],
                )
            ]
        )
        # print("from_currency => {}, to_currency => {}, valuation_date => {}".format(from_currency,to_currency,valuation_date))
        # # 1. check in cache

        # # 2. check in DB

        # # 3. call API

        # print("args => {}".format(args))
        # print("kwargs => {}".format(kwargs))
        # print(request)
        # print(request.query_params.keys())
        # print(type(request.query_params))

        # queryset = CurrencyExchangeRate.objects.filter(source_currency__code=from_currency,exchanged_currency__code=to_currency,rate_value=arrow.Arrow()).first()
        # serializer = self.get_serializer(queryset, many=True)
        # print(type(serializer.data))
        # print(serializer.data)
        # print(len(serializer.data))
        # return Response(serializer.data)

    # def get_queryset(self):
    #     return super().get_queryset()


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
