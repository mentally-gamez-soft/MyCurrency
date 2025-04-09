"""Create predefined echange rate providers."""

import logging

from django.core.management.base import BaseCommand

from mycurrency_exchange_rates.models import ExchangeRateProvider


def add_providers():
    """Create the 2 providers in the DB."""
    ExchangeRateProvider(
        provider_name="currencybeacon",
        priority=1,
        active_flag=True,
        active_status=True,
    ).save()
    ExchangeRateProvider(
        provider_name="mock",
        priority=10,
        active_flag=True,
        active_status=False,
    ).save()


class Command(BaseCommand):
    """Provide a CLI option for manage.py to create predefined exchange rates providers.

    Args:
        BaseCommand (_type_): _description_
    """

    help = "Creates 2 exchange rate providers currencybeacon and mock."

    def handle(self, *args, **options):
        """Handle the manage py command."""
        add_providers()

        logging.info("Added providers.")
