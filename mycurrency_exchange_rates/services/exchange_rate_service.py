"""Define the generic service interface of the app."""

import logging

import arrow
from pybreaker import CircuitBreaker

from mycurrency_exchange_rates.models import ExchangeRateProvider
from mycurrency_exchange_rates.services.database_managers.managers import (
    set_next_provider_by_priority,
)

from .providers_service import (
    CURRENCY_BEACON_PROVIDER_NAME,
    MOCK_PROVIDER_NAME,
    currency_beacon_provider,
    mock_provider,
)

logger = logging.getLogger(__name__)


def get_current_provider_service():
    """Determine the current active provider."""
    current_provider_name = ExchangeRateProvider.objects.filter(
        active_status=True
    ).first()
    logger.info("The current provider is {}".format(current_provider_name))

    if not current_provider_name:
        return None

    if CURRENCY_BEACON_PROVIDER_NAME in current_provider_name.provider_name:
        logger.info("Use of currency beacon provider")
        return currency_beacon_provider
    elif MOCK_PROVIDER_NAME in current_provider_name.provider_name:
        logger.info("Use of mock provider")
        return mock_provider


def get_exchange_rate_data(
    source_currency, exchanged_currency, valuation_date, provider
):
    """Declare the adapter to get a currency conversion."""
    if not provider:
        return {
            "status": "ko",
            "message": (
                "No rate exchange provider is available at the moment !"
            ),
        }

    a_now = arrow.utcnow()
    if valuation_date >= a_now.shift(days=1).date():
        return {
            "status": "ko",
            "message": "A rate value cannot be read in the future",
        }

    try:
        return provider(source_currency, exchanged_currency, valuation_date)
    except CircuitBreaker.Error:
        set_next_provider_by_priority()


def get_currency_rates_list(source_currency, from_date, to_date, provider):
    """Declare the adapter to get a time series list of currency conversions."""
    return provider(source_currency, from_date, to_date)
