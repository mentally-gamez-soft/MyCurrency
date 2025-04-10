"""Declare the views and endpoints."""

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from pybreaker import CircuitBreaker
from rest_framework import viewsets
from rest_framework.response import Response

from mycurrency_exchange_rates.services.database_managers.managers import (
    get_conversion_from_database,
    store_conversion_to_DB,
)
from mycurrency_exchange_rates.services.exchange_rate_service import (
    get_current_provider_service,
    get_exchange_rate_data,
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

        # data available in the backend ?
        result = get_conversion_from_database(
            from_currency=from_currency,
            to_currency=to_currency,
            valuation_date=arrow_date["arrow_date"],
        )
        if "message" in result.keys():
            # go to search data in the active current provider
            provider = get_current_provider_service()
            response = get_exchange_rate_data(
                source_currency=from_currency,
                exchanged_currency=to_currency,
                valuation_date=arrow_date["arrow_date"],
                provider=provider,
            )
            if "ok" in response["status"]:
                store_conversion_to_DB(
                    from_currency_code=from_currency,
                    to_currency_code=to_currency,
                    rate_value=response["rate_value"],
                    valuated_date=arrow_date["arrow_date"],
                )
            return Response([response])
        else:
            return Response([result])


class CurrencyViewSet(viewsets.ModelViewSet):
    """Define API endpoint to get the currency."""

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    def list(self, request, *args, **kwargs):
        """Get all the Currencies."""
        queryset = Currency.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
