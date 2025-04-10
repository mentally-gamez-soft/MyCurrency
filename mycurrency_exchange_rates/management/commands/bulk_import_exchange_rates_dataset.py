"""Import a dataset of rates for various currencies."""

import asyncio
import logging
import os
from decimal import Decimal

import aiohttp
import arrow
from django.core.management.base import BaseCommand

from mycurrency_exchange_rates.models import Currency, CurrencyExchangeRate
from mycurrency_exchange_rates.services.providers_service.currency_beacon_provider import (
    CURRENCY_RATES_URL,
)

currencies = ["CHF", "GBP", "EUR", "USD"]


def record_data(list_exchange_rates: list):
    """Store the exchange rate results in the database.

    Args:
        list_exchange_rates (list): the list of exchange rates coming from the provider api call.
    """
    for i in range(0, len(currencies)):
        date_keys = list_exchange_rates[i]["response"].keys()
        for date_key in date_keys:
            dest_currency_keys = list_exchange_rates[i]["response"][
                date_key
            ].keys()
            for currency_key in dest_currency_keys:
                rate_value = list_exchange_rates[i]["response"][date_key][
                    currency_key
                ]

                CurrencyExchangeRate.objects.create(
                    source_currency=Currency.objects.filter(
                        code=currencies[i]
                    ).first(),
                    exchanged_currency=Currency.objects.filter(
                        code=currency_key
                    ).first(),
                    valuation_date=arrow.get(date_key, "YYYY-MM-DD").date(),
                    rate_value=Decimal(rate_value),
                )


def get_api_calls(session, from_date: arrow.Arrow, to_date: arrow.Arrow):
    """Put all the api calls in a bucket to rigger all of themn at once.

    Args:
        session (ClientSession): the session for the async call
        from_date (arrow.Arrow): the start date for the bulk data
        to_date (arrow.Arrow): the end date for the bulk data

    Returns:
        list: list of bulk api calls to trigger.
    """
    api_calls = []
    for src_currency in currencies:
        api_calls.append(
            session.get(
                CURRENCY_RATES_URL.format(
                    os.getenv("CURRENCY_BEACON_API_KEY"),
                    src_currency,
                    from_date.format("YYYY-MM-DD"),
                    to_date.format("YYYY-MM-DD"),
                    ",".join(
                        [
                            dest_currency
                            for dest_currency in currencies
                            if dest_currency != src_currency
                        ]
                    ),
                ),
                ssl=False,
            )
        )

    return api_calls


async def retrieve_exchange_rates(
    from_date: arrow.Arrow, to_date: arrow.Arrow
) -> dict:
    """Lookup for the exchange rates in a date range.

    Args:
        from_date (arrow.Arrow): the start date for the bulk data
        to_date (arrow.Arrow): the end date for the bulk data
    """
    results = []
    async with aiohttp.ClientSession() as session:
        api_calls = get_api_calls(session, from_date, to_date)
        responses = await asyncio.gather(*api_calls)
        for response in responses:
            results.append(await response.json())

    return results


def import_bulk_data():
    """Import historic exchange data for 4 currencies."""
    from_date = arrow.Arrow(2024, 3, 1)
    # to_date = arrow.utcnow()
    to_date = arrow.Arrow(2024, 3, 31)

    if to_date < from_date:
        raise Exception("The start date can not be higher than the end date !")

    results = asyncio.run(retrieve_exchange_rates(from_date, to_date))
    logging.info(results)
    record_data(list_exchange_rates=results)


class Command(BaseCommand):
    """Provide a CLI option for manage.py to import exchange rates in a range of dates for a list of currencies.

    Args:
        BaseCommand (_type_): _description_
    """

    help = "Import historical bulk data."

    def handle(self, *args, **options):
        """Handle the manage py command."""
        import_bulk_data()

        # logging.info("Added providers.")
