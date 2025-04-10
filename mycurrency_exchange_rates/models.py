"""Declare the models for the application mycurrency exchange rate."""

from django.db import models


class ExchangeRateProvider(models.Model):
    """Define a Currency Provider object."""

    provider_name = models.CharField(max_length=50, db_index=True, unique=True)
    priority = models.IntegerField(null=False)
    active_flag = models.BooleanField(default=False, null=False)
    active_status = models.BooleanField(default=False, null=False)

    def __str__(self):
        """Add readibility for the model."""
        return "Provider: {} - priority: {}".format(
            self.provider_name, self.priority
        )

    class Meta:
        """Set properties about the model and its behaviour."""

        ordering = ["-priority"]
        verbose_name = "Provider for exchange rates"
        verbose_name_plural = "Providers for exchange rates"


class Currency(models.Model):
    """Define the Currency object."""

    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, db_index=True)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        """Add readibility for the model."""
        return "Currency - name: {} - code: {}".format(self.name, self.code)

    class Meta:
        """Set properties about the model and its behaviour."""

        verbose_name = "Currency"
        verbose_name_plural = "Currencies"


class CurrencyExchangeRate(models.Model):
    """Define the relationship between 2 currencies and their rate."""

    source_currency = models.ForeignKey(
        Currency, related_name="exchanges", on_delete=models.CASCADE
    )
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(
        db_index=True, decimal_places=6, max_digits=18
    )

    def __str__(self):
        """Add readibility for the model."""
        return "{} -> {} - {} - rate: {}".format(
            self.source_currency.code,
            self.exchanged_currency.code,
            self.valuation_date,
            self.rate_value,
        )

    class Meta:
        """Set properties about the model and its behaviour."""

        ordering = ["source_currency"]
        verbose_name = "Currency Exchange Rate"
