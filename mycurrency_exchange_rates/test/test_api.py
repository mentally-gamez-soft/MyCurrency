"""Define the test suite for the DRF API."""

import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from mycurrency_exchange_rates.models import Currency


class CurrencyExchangeRateTest(APITestCase):
    """Declare the tests for endpoints related to currency exchange rate valuation."""

    def test_rate_conversion_not_possible_without_currency_source(self):
        """Verify that the conversion rate endpoint canot answer if the source currency is missing."""
        url = reverse("currencyexchangerate-list")

        response = self.client.get(url, data={"to_currency": 3})
        # response.render()
        # json_response = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "The endpoint /currency-coverter does not exist.",
        )
        self.assertTrue(
            "The currency code source must be specified !"
            in response.content.decode(),
            "The endpoint /currency-converter is not properly configured !",
        )

    def test_rate_conversion_not_possible_without_currency_destination(self):
        """Verify that the conversion rate endpoint cannot answer if the destiuation currency is missing."""
        url = reverse("currencyexchangerate-list")

        response = self.client.get(url, data={"from_currency": 2})

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "The endpoint /currency-coverter does not exist.",
        )
        self.assertTrue(
            "The currency code destination must be specified !"
            in response.content.decode(),
            "The endpoint /currency-converter is not properly configured !",
        )

    def test_read_rate_conversion(self):
        """Verify the declaration of endpoint for exchange rate."""
        url = reverse("currencyexchangerate-list")

        response = self.client.get(
            url, data={"from_currency": 2, "to_currency": 3}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "The endpoint /currency-coverter does not exist.",
        )


class CurrencyTest(APITestCase):
    """Declare the tests for endpoints related to currency."""

    def test_read_currencies(self):
        """Verify the declaration for currencies list end point."""
        url = reverse("currency-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "The endpoint /currency does not exist.",
        )

    def test_create_currency(self):
        """Verify the endpoint declaration for the creation of a new currency."""
        self.__create_new_currency()

    def test_update_currency(self):
        """Verify the update endpoint for a currency."""
        self.__create_new_currency()

        obj = Currency.objects.filter(pk=1).first()

        payload = {"code": "GBP", "name": "Sterling Pound", "symbol": "M"}
        url = reverse("currency-detail", kwargs={"pk": obj.pk})

        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        obj = Currency.objects
        self.assertEqual(obj.count(), 1, "The currency has not been updated")
        self.assertEqual(
            obj.get().code, "GBP", "The currency has not been updated"
        )
        self.assertEqual(
            obj.get().name,
            "Sterling Pound",
            "The currency has not been updated",
        )
        self.assertEqual(
            obj.get().symbol, "M", "The currency has not been updated"
        )

    def test_delete_currency(self):
        """Verify the deletion endpoint for a currency."""
        self.__create_new_currency()

        obj = Currency.objects.filter(pk=1).first()
        url = reverse("currency-detail", kwargs={"pk": obj.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        obj = Currency.objects
        self.assertEqual(
            obj.count(), 0, "The currency was not deleted successfully."
        )

    def __create_new_currency(self):
        payload = {"code": "GBP", "name": "Sterling Pound", "symbol": "L"}
        url = reverse("currency-list")

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        obj = Currency.objects
        self.assertEqual(obj.count(), 1, "The currency has not been created")
        self.assertEqual(
            obj.get().code, "GBP", "The currency has not been created"
        )
        self.assertEqual(
            obj.get().name,
            "Sterling Pound",
            "The currency has not been created",
        )
        self.assertEqual(
            obj.get().symbol, "L", "The currency has not been created"
        )
