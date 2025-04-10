"""Define the provider currency beacon."""

import asyncio
import os

import aiohttp
import arrow

from mycurrency_exchange_rates.models import ExchangeRateProvider

PROVIDER_NAME = "currencybeacon"
CURRENCY_RATES_URL = "https://api.currencybeacon.com/v1/timeseries?api_key={}&base={}&start_date={}&end_date={}&symbols={}"
CONVERSION_URL = "https://api.currencybeacon.com/v1/convert?api_key={}&from={}&to={}&amount={}"
CONVERSION_HISTORICAL_URL = "https://api.currencybeacon.com/v1/historical?api_key={}&base={}&date={}&symbols={}"


def currency_beacon_provider(
    source_currency, exchanged_currency, valuation_date
) -> dict:
    """Define the concrete function when the currency beacon provider is called."""
    # 1. check in cache

    # 2. check in DB

    # 3. call API
    if valuation_date == arrow.utcnow().date():
        return asyncio.run(
            request_api_convert(source_currency, exchanged_currency)
        )
    else:
        return asyncio.run(
            request_api_history(
                source_currency, exchanged_currency, valuation_date
            )
        )


async def request_api_convert(source_currency, exchanged_currency) -> dict:
    """Define the api request for standard conversion currency."""
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            CONVERSION_URL.format(
                os.getenv("CURRENCY_BEACON_API_KEY"),
                source_currency,
                exchanged_currency,
                "1.0",
            ),
            ssl=False,
        )
        response_json = await response.json()

    return {
        "status": "ok",
        "provider": PROVIDER_NAME,
        "api-fct": "request_api_convert",
        "from_currency": source_currency,
        "to_currency": exchanged_currency,
        "valuation_date": response_json["response"]["date"],
        "rate_value": response_json["response"]["value"],
    }


async def request_api_history(
    source_currency, exchanged_currency, valuation_date: arrow.Arrow
) -> dict:
    """Define the api request for standard conversion currency for a specific day."""
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            CONVERSION_HISTORICAL_URL.format(
                os.getenv("CURRENCY_BEACON_API_KEY"),
                source_currency,
                valuation_date.format("YYYY-MM-DD"),
                exchanged_currency,
            ),
            ssl=False,
        )
        response_json = await response.json()

    return {
        "status": "ok",
        "provider": PROVIDER_NAME,
        "api-fct": "request_api_history",
        "from_currency": source_currency,
        "to_currency": exchanged_currency,
        "valuation_date": response_json["response"]["date"],
        "rate_value": response_json["response"]["rates"][exchanged_currency],
    }


async def request_time_series_api(
    from_currency,
    to_currencies: list,
    from_date: arrow.Arrow,
    to_date: arrow.Arrow,
):
    """Define the currency beacon request for time series currency call."""
    symbols = ",".join(to_currencies)

    async with aiohttp.ClientSession() as session:
        response = await session.get(
            CURRENCY_RATES_URL.format(
                os.getenv("CURRENCY_BEACON_API_KEY"),
                from_currency,
                from_date.format("YYYY-MM-DD"),
                to_date.format("YYYY-MM-DD"),
                symbols,
            ),
            ssl=False,
        )
        response_json = await response.json()

    result = response_json["response"]
    result["status"] = "ok"
    result["provider"] = PROVIDER_NAME
    result["from_currency"] = from_currency

    return result
