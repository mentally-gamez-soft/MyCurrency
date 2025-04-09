"""Tool for initializing the database with the currencies CHF, USD, EUR, GBP."""

import logging

from django.core.management.base import BaseCommand

from mycurrency_exchange_rates.models import Currency


def add_currencies():
    """Create the currencies into DB."""
    currency = Currency(code="EUR", name="Euro", symbol="€")
    currency.save()

    currency = Currency(code="CHF", name="Swiss franc", symbol="Fr.")
    currency.save()

    currency = Currency(code="USD", name="US Dollar", symbol="$")
    currency.save()

    currency = Currency(code="GBP", name="Pound Sterling", symbol="£")
    currency.save()


class Command(BaseCommand):
    """Provide a CLI option for manage.py to ingest currencies in the DB.

    Args:
        BaseCommand (_type_): _description_
    """

    help = "Creates a batch of fake currencies."

    def handle(self, *args, **options):
        """Handle the manage py command."""
        add_currencies()

        logging.info("Added currencies.")
