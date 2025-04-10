"""Configure the administration console."""

from django.contrib import admin

from .models import Currency, CurrencyExchangeRate, ExchangeRateProvider

admin.site.register(ExchangeRateProvider)
admin.site.register(Currency)
admin.site.register(CurrencyExchangeRate)

admin.site.site_header = "Back office for My Currency App"
admin.site.site_title = "My Currency App web admin"
admin.site.index_title = "Administration"
