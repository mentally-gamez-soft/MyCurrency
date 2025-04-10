"""Define the provider currency beacon."""

import asyncio
import os

import aiohttp
import arrow
from pybreaker import CircuitBreaker
from tenacity import retry, stop_after_attempt, wait_exponential

from mycurrency_exchange_rates.models import ExchangeRateProvider

PROVIDER_NAME = "currencybeacon"
CURRENCY_RATES_URL = "https://api.currencybeacon.com/v1/timeseries?api_key={}&base={}&start_date={}&end_date={}&symbols={}"
CONVERSION_URL = "https://api.currencybeacon.com/v1/convert?api_key={}&from={}&to={}&amount={}"
CONVERSION_HISTORICAL_URL = "https://api.currencybeacon.com/v1/historical?api_key={}&base={}&date={}&symbols={}"

circuit_breaker = CircuitBreaker(fail_max=5, reset_timeout=120)


@circuit_breaker
def currency_beacon_provider(
    source_currency, exchanged_currency, valuation_date
) -> dict:
    """Define the concrete function when the currency beacon provider is called."""
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


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
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


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
async def request_api_history(
    source_currency, exchanged_currency, valuation_date: arrow.Arrow
) -> dict:
    """Define the api request for standard conversion currency for a specific day."""
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            CONVERSION_HISTORICAL_URL.format(
                os.getenv("CURRENCY_BEACON_API_KEY"),
                source_currency,
                # valuation_date.format("YYYY-MM-DD"),
                valuation_date,
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
) -> dict:
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
