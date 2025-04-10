"""Define the application configuration."""

from django.apps import AppConfig


class MycurrencyExchangeRatesConfig(AppConfig):
    """Define the application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "mycurrency_exchange_rates"
    verbose_name = "My Currency App"
