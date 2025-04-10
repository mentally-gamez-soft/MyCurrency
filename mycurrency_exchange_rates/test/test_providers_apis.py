"""Define the tests suits for the raw APIs."""

import asyncio
from decimal import Decimal

import arrow
import vcr
from django.test import TestCase

from mycurrency_exchange_rates.models import ExchangeRateProvider
from mycurrency_exchange_rates.services.exchange_rate_service import (
    get_current_provider,
    get_exchange_rate_data,
)
from mycurrency_exchange_rates.services.providers_service import (
    currency_beacon_provider,
    mock_provider,
    request_time_series_currency_beacon_api,
    request_time_series_mock_api,
)


class TestCurrencyBeaconProvider(TestCase):
    """Define the tests suite for the provider currency beacon."""

    def setUp(self):
        """Prepare the dataset before each test."""
        self.source_currency = "CHF"
        self.destination_currency = "EUR"
        self.valuation_date = arrow.utcnow().date()

    @vcr.use_cassette(
        "mycurrency_exchange_rates/test/fixtures/vcr_cassettes/TestCurrencyBeaconProvider-test_standard_api.yaml"
    )
    def test_convert_api(self):
        """Verify the endpoint for the conversion of a currency."""
        response = currency_beacon_provider(
            source_currency=self.source_currency,
            exchanged_currency=self.destination_currency,
            valuation_date=self.valuation_date,
        )
        self.assertEqual(response["status"], "ok", "An error occured !")
        self.assertEqual(
            response["api-fct"], "request_api_convert", "An error occured !"
        )
        self.assertGreater(
            response["rate_value"], 0, "The rate value is incorrect !"
        )

    @vcr.use_cassette(
        "mycurrency_exchange_rates/test/fixtures/vcr_cassettes/TestCurrencyBeaconProvider-test_historic_api.yaml"
    )
    def test_convert_history_api(self):
        """Verify the endpoint for the conversion of a currency for a specific day."""
        self.valuation_date = arrow.Arrow(2025, 2, 13)
        response = currency_beacon_provider(
            source_currency=self.source_currency,
            exchanged_currency=self.destination_currency,
            valuation_date=self.valuation_date,
        )
        self.assertEqual(response["status"], "ok", "An error occured !")
        self.assertEqual(
            response["api-fct"], "request_api_history", "An error occured !"
        )
        self.assertGreater(
            response["rate_value"], 0, "The rate value is incorrect !"
        )

    def test_request_time_series_api(self):
        """Verify the endpoint to retrieve the time series for a secific currency."""
        from_currency = "GBP"
        to_currencies = ["CHF", "USD", "EUR"]
        from_date = arrow.Arrow(2025, 1, 1)
        to_date = arrow.Arrow(2025, 2, 23)
        response = asyncio.run(
            request_time_series_currency_beacon_api(
                from_currency=from_currency,
                to_currencies=to_currencies,
                from_date=from_date,
                to_date=to_date,
            )
        )
        self.assertEqual(
            response["status"], "ok", "The expected status is wrong"
        )


class TestMockProvider(TestCase):
    """Define the tests suite for the provider mock."""

    def setUp(self):
        """Prepare the dataset before each test."""
        self.source_currency = "CHF"
        self.destination_currency = "EUR"
        self.valuation_date = arrow.utcnow().date()

    def test_api(self):
        """Verify the endpoint for the conversion of a currency."""
        response = mock_provider(
            source_currency=self.source_currency,
            exchanged_currency=self.destination_currency,
            valuation_date=self.valuation_date,
        )
        self.assertEqual(response["status"], "ok", "An error occured !")
        self.assertGreater(
            Decimal(response["rate_value"]),
            Decimal(0.0),
            "The rate value is incorrect !",
        )

    def test_cant_value_rate_in_future_dates(self):
        """Verify the endpoint for the conversion of a currency."""
        self.valuation_date = arrow.utcnow().shift(days=3).date()
        response = mock_provider(
            source_currency=self.source_currency,
            exchanged_currency=self.destination_currency,
            valuation_date=self.valuation_date,
        )
        self.assertEqual(response["status"], "ko", "An error occured !")
        self.assertEqual(
            response["message"],
            "The rate cant be retrieved from the future !",
            "An error occured !",
        )

    def test_request_time_series_api(self):
        """Verify the endpoint to retrieve the time series for a secific currency."""
        start_date = arrow.Arrow(2025, 1, 1)
        end_date = arrow.Arrow.utcnow()

        response = request_time_series_mock_api(
            from_currency=self.source_currency,
            to_currencies=["EUR", "USD", "GBP"],
            from_date=start_date,
            to_date=end_date,
        )
        self.assertEqual(response["status"], "ok", "An error occured !")
        self.assertIsInstance(
            response[start_date.format("YYYY-MM-DD")],
            dict,
            "The rates time series is incorrect !",
        )


class TestAdapterProvider(TestCase):
    """Define the tests suite for the adapter calls."""

    def setUp(self):
        """Prepare the dataset before each test."""
        self.source_currency = "CHF"
        self.destination_currency = "EUR"
        self.valuation_date = arrow.utcnow().date()

        self.mock_provider = ExchangeRateProvider.objects.create(
            provider_name="mock",
            priority=10,
            active_flag=True,
            active_status=False,
        )
        self.currency_beacon_provider = ExchangeRateProvider.objects.create(
            provider_name="currencybeacon",
            priority=1,
            active_flag=True,
            active_status=False,
        )

        self.mock_provider.save()
        self.currency_beacon_provider.save()

    def test_exchange_rate_data_no_provider_set(self):
        """Verify the endpoint for the conversion of a currency when no provider is available."""
        provider = get_current_provider()

        response = get_exchange_rate_data(
            source_currency=self.source_currency,
            exchanged_currency=self.destination_currency,
            valuation_date=self.valuation_date,
            provider=provider,
        )

        self.assertIsNotNone(response, "The returned value is incorrect !")
        self.assertEqual(
            response["status"],
            "ko",
            "When no provider is set, we expected a ko status !",
        )
        self.assertEqual(
            response["message"],
            "No rate exchange provider is available at the moment !",
        )

    @vcr.use_cassette(
        "mycurrency_exchange_rates/test/fixtures/vcr_cassettes/TestAdapterProvider-test_exchange_rate_data_currencybeacon_provider_set.yaml"
    )
    def test_exchange_rate_data_currencybeacon_provider_set(self):
        """Verify the endpoint for the conversion of a currency with currency beacon as the active provider."""
        self.currency_beacon_provider.active_status = True
        self.currency_beacon_provider.save()
        provider = get_current_provider()

        response = get_exchange_rate_data(
            source_currency=self.source_currency,
            exchanged_currency=self.destination_currency,
            valuation_date=self.valuation_date,
            provider=provider,
        )

        self.assertIsNotNone(response, "The returned value is incorrect !")
        self.assertEqual(
            response["status"],
            "ok",
            "When a provider is set, we expected a ok status !",
        )
        self.assertEqual(
            response["provider"],
            "currencybeacon",
            "The expected provider is incorrect !",
        )
        self.assertGreater(
            response["rate_value"], 0, "The rate value is incorrect !"
        )

    def test_exchange_rate_data_mock_provider_set(self):
        """Verify the endpoint for the conversion of a currency with mock as the active provider."""
        self.mock_provider.active_status = True
        self.mock_provider.save()
        provider = get_current_provider()

        response = get_exchange_rate_data(
            source_currency=self.source_currency,
            exchanged_currency=self.destination_currency,
            valuation_date=self.valuation_date,
            provider=provider,
        )

        self.assertIsNotNone(response, "The returned value is incorrect !")
        self.assertEqual(
            response["status"],
            "ok",
            "When a provider is set, we expected a ok status !",
        )
        self.assertEqual(
            response["provider"],
            "mock",
            "The expected provider is incorrect !",
        )
        self.assertGreater(
            Decimal(response["rate_value"]),
            Decimal(0.0),
            "The rate value is incorrect !",
        )
