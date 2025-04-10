"""Define the provider mock."""

import arrow
from faker import Faker

PROVIDER_NAME = "mock"


def mock_provider(source_currency, exchanged_currency, valuation_date) -> dict:
    """Define the concrete function when the mock provider is called."""
    # 1. check in cache

    # 2. check in DB

    # 3. call API
    if valuation_date >= arrow.Arrow.utcnow().shift(days=1).date():
        return {
            "status": "ko",
            "provider": PROVIDER_NAME,
            "message": "The rate cant be retrieved from the future !",
        }

    return request_api(source_currency, exchanged_currency, valuation_date)


def request_api(source_currency, exchanged_currency, valuation_date):
    """Define the mock request for standard conversion currency call."""
    fake = Faker()
    rate_value = fake.numerify("#.######")

    return {
        "status": "ok",
        "provider": PROVIDER_NAME,
        "from_currency": source_currency,
        "to_currency": exchanged_currency,
        "valuation_date": valuation_date,
        "rate_value": rate_value,
    }


def request_time_series_api(
    from_currency,
    to_currencies: list,
    from_date: arrow.Arrow,
    to_date: arrow.Arrow,
):
    """Define the mock request for time series currency call."""
    response = {
        "status": "ok",
        "provider": PROVIDER_NAME,
        "from_currency": from_currency,
    }
    fake = Faker()

    for a in arrow.Arrow.span_range("day", from_date, to_date):
        response[a[0].format("YYYY-MM-DD")] = {}
        for target_currency in to_currencies:
            response[a[0].format("YYYY-MM-DD")][target_currency] = (
                fake.numerify("#.######")
            )
    return response
