"""Declare the service providers module."""

from .currency_beacon_provider import (
    PROVIDER_NAME as CURRENCY_BEACON_PROVIDER_NAME,
)
from .currency_beacon_provider import (
    currency_beacon_provider,
)
from .currency_beacon_provider import (
    request_time_series_api as request_time_series_currency_beacon_api,
)
from .mock_provider import PROVIDER_NAME as MOCK_PROVIDER_NAME
from .mock_provider import (
    mock_provider,
)
from .mock_provider import (
    request_time_series_api as request_time_series_mock_api,
)

__all_ = [
    "currency_beacon_provider",
    "CURRENCY_BEACON_PROVIDER_NAME",
    "mock_provider",
    "MOCK_PROVIDER_NAME",
    "request_time_series_mock_api",
    "request_time_series_currency_beacon_api",
]
