"""Create predefined echange rate providers."""

import logging

from django.core.management.base import BaseCommand

from mycurrency_exchange_rates.models import ExchangeRateProvider


def add_providers():
    """Create the 4 providers in the DB."""
    ExchangeRateProvider(
        provider_name="currencybeacon 1",
        priority=1,
        active_flag=True,
        active_status=True,
    ).save()
    ExchangeRateProvider(
        provider_name="mock 1",
        priority=10,
        active_flag=True,
        active_status=False,
    ).save()
    ExchangeRateProvider(
        provider_name="currencybeacon 2",
        priority=20,
        active_flag=True,
        active_status=False,
    ).save()
    ExchangeRateProvider(
        provider_name="mock 2",
        priority=30,
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
