"""Define the test suites for the service managers (cache, db, circuit breaker...)."""

from decimal import Decimal

import arrow
from django.test import TestCase
from faker import Faker

from mycurrency_exchange_rates.models import Currency, CurrencyExchangeRate
from mycurrency_exchange_rates.services.database_managers.managers import (
    exists_currency_rates_during_interval_for_pair_of_currencies,
    get_conversion_from_database,
    get_number_of_consecutive_days,
    is_valid_currency,
)


class TestDbManagers(TestCase):
    "Declare the tests suite for the database service manager."

    def setUp(self):
        """Prepare the dataset before each test."""
        self.source_currency = Currency.objects.create(
            code="FRA", name="Franc", symbol="F"
        )
        self.dest_currency = Currency.objects.create(
            code="CFA", name="Franc CFA", symbol="SGA"
        )
        self.rate_value = "100.300021"
        self.valuation_date = arrow.utcnow().date()
        CurrencyExchangeRate.objects.create(
            source_currency=self.source_currency,
            exchanged_currency=self.dest_currency,
            rate_value=self.rate_value,
            valuation_date=self.valuation_date,
        )

    def test_is_valid_currency(self):
        """Verify the validity of a currency in the DB."""
        self.assertTrue(is_valid_currency(self.source_currency.code))

    def test_is_not_valid_currency(self):
        """Verify the validity of a currency in the DB."""
        self.assertFalse(is_valid_currency("GBP"))

    def test_conversion_from_database(self):
        """Verify the conversion of a currency in the DB."""
        amount = 2
        result = get_conversion_from_database(
            from_currency=self.source_currency.code,
            to_currency=self.dest_currency.code,
            valuation_date=self.valuation_date,
            amount=amount,
        )
        self.assertIsNotNone(result, "The conversion failed !")
        self.assertTrue(
            result["status"] == "ok", "The expected status is not matching !"
        )
        self.assertEqual(
            result["converted_amount"],
            str(Decimal(self.rate_value) * amount),
            "The converted amount is incorrect !",
        )

    def test_conversion_from_database_available_for_same_day_at_different_time(
        self,
    ):
        """Verify the conversion of a currency in the DB."""
        amount = 3
        valuation_date = arrow.utcnow().shift(hours=-3).date()
        result = get_conversion_from_database(
            from_currency=self.source_currency.code,
            to_currency=self.dest_currency.code,
            valuation_date=valuation_date,
            amount=amount,
        )
        self.assertIsNotNone(result, "The conversion failed !")
        self.assertTrue(
            result["status"] == "ok", "The expected status is not matching !"
        )
        self.assertEqual(
            result["converted_amount"],
            str(Decimal(self.rate_value) * amount),
            "The converted amount is incorrect !",
        )

    def test_no_conversion_from_database_available_for_different_date(self):
        """Verify the conversion of a currency in the DB."""
        amount = 2
        valuation_date = arrow.utcnow().shift(days=-3).date()
        result = get_conversion_from_database(
            from_currency=self.source_currency.code,
            to_currency=self.dest_currency.code,
            valuation_date=valuation_date,
            amount=amount,
        )
        self.assertIsNotNone(result, "The conversion failed !")
        self.assertTrue(
            result["status"] == "ok", "The expected status is not matching !"
        )
        self.assertTrue(
            "No rate available" in result["message"],
            "The returned message is invalid !",
        )

    def test_no_conversion_from_database_available_with_date_in_future(self):
        """Verify the conversion of a currency in the DB."""
        amount = 2
        valuation_date = arrow.utcnow().shift(days=1).date()
        result = get_conversion_from_database(
            from_currency=self.source_currency.code,
            to_currency=self.dest_currency.code,
            valuation_date=valuation_date,
            amount=amount,
        )
        self.assertIsNotNone(result, "The conversion failed !")
        self.assertTrue(
            result["status"] == "ko", "The expected status is not matching !"
        )
        self.assertTrue(
            "A rate value cannot be read in the future" in result["message"],
            "The returned message is invalid !",
        )

    def test_get_number_of_consecutive_days_available_for_a_pair_of_currencies(
        self,
    ):
        """Verify the number of consecutive days existing for a pair of currency in the DB."""
        # set the date interval (51 days)
        from_date = arrow.Arrow(2025, 1, 1)
        to_date = arrow.Arrow(2025, 2, 20)
        number_days = len(
            list(arrow.Arrow.span_range("day", from_date, to_date))
        )  # number_days = (to_date - from_date).days

        self.__generate_bulk_value_rates_in_DB(
            from_date=from_date, to_date=to_date
        )  # create all thew currencies and exchange rate values on this time interval

        from_currency = Currency.objects.filter(pk=1).first().code
        to_currency = Currency.objects.filter(pk=2).first().code

        nb_days_consecutive = get_number_of_consecutive_days(
            from_currency=from_currency,
            to_currency=to_currency,
            from_date=from_date.date(),
            to_date=to_date.date(),
        )
        self.assertEqual(
            number_days,
            nb_days_consecutive,
            "The number of days is unexpected !",
        )

    def test_has_currency_rates_during_interval_for_pair_of_currencies(self):
        """Verify the number of consecutive days existing for a pair of currency in the DB."""
        # set the date interval (20 days)
        from_date = arrow.Arrow(2025, 1, 1)
        to_date = arrow.Arrow(2025, 1, 20)

        self.__generate_bulk_value_rates_in_DB(
            from_date=from_date, to_date=to_date
        )  # create all thew currencies and exchange rate values on this time interval

        from_currency_code = Currency.objects.filter(pk=1).first().code
        to_currency_code = Currency.objects.filter(pk=2).first().code

        self.assertTrue(
            exists_currency_rates_during_interval_for_pair_of_currencies(
                from_currency_code=from_currency_code,
                to_currency_code=to_currency_code,
                from_date=from_date,
                to_date=to_date,
            )
        )

    def __generate_bulk_currencies_in_DB(self) -> None:
        fake = Faker()
        fakes = []
        for _ in range(1, 30):
            currency_code = fake.currency_code
            currency_name = fake.currency_name
            currency_symbol = fake.currency_symbol
            t_fake = (currency_code, currency_name, currency_symbol)
            if t_fake not in fakes:
                fakes.append(t_fake)

        for currency in fakes:
            Currency.objects.create(
                code=currency[0], name=currency[1], symbol=currency[2]
            )

    def __generate_bulk_value_rates_in_DB(self, from_date, to_date):
        # start by creating the list of currencies.
        self.__generate_bulk_currencies_in_DB()

        currencies = Currency.objects.all()
        fake = Faker()

        for base_currency in currencies:
            for dest_currency in currencies:
                if base_currency != dest_currency:
                    # let's create a fake historic set of rate values for the couple source currency/dest currency
                    for a_tuple in arrow.Arrow.span_range(
                        "day", from_date, to_date
                    ):
                        CurrencyExchangeRate.objects.create(
                            source_currency=base_currency,
                            exchanged_currency=dest_currency,
                            valuation_date=a_tuple[0].date(),
                            rate_value=fake.numerify("#.######"),
                        )
