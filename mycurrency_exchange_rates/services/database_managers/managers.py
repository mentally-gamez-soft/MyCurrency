"""Define the databse service managers."""

import arrow

from mycurrency_exchange_rates.models import Currency, CurrencyExchangeRate


def is_valid_currency(currency_code: str) -> Currency | None:
    """Indicate if a currency exist in the database.

    Args:
        currency_code (str): The code for the currency to lookup.

    Returns:
        bool: Return the currency object or None.
    """
    return Currency.objects.filter(code=currency_code).first()


def get_conversion_from_database(
    from_currency, to_currency, valuation_date=arrow.utcnow().date(), amount=1
) -> dict:
    """Retrieve the rate values for a couple base currency to target currency.

    Args:
        from_currency (str): The code of the base currency
        to_currency (_type_): The code for the target currency
        valuation_date (date, optional): date for which to find a rate value. Defaults to arrow.utcnow().date().
        amount (int, optional): The amount to translate if indicated. Defaults to 1.

    Returns:
        dict: A dictionary containing the status, a recap of the input, the rate value and the calculated amount.
    """
    if valuation_date >= arrow.utcnow().shift(days=1).date():
        return {
            "status": "ko",
            "message": "A rate value cannot be read in the future",
        }

    if not is_valid_currency(from_currency):
        return {
            "status": "ko",
            "message": (
                "The specified source currency code {} is not available at the"
                " moment.".format(from_currency)
            ),
        }

    if not is_valid_currency(to_currency):
        return {
            "status": "ko",
            "message": (
                "The specified destination currency code {} is not available"
                " at the moment.".format(to_currency)
            ),
        }

    conversion_rate = (
        CurrencyExchangeRate.objects.filter(
            source_currency__code=from_currency,
            exchanged_currency__code=to_currency,
            valuation_date=valuation_date,
        )
        .select_related()
        .first()
    )
    if conversion_rate:
        converted_amount = conversion_rate.rate_value * amount
        result = dict(
            status="ok",
            from_currency=from_currency,
            to_currency=to_currency,
            rate_value=str(conversion_rate.rate_value),
            amount=amount,
            converted_amount=str(converted_amount),
        )
        return result
    else:
        return {
            "status": "ok",
            "message": "No rate available for {} -> {} at {}.".format(
                from_currency, to_currency, valuation_date
            ),
        }


def get_number_of_consecutive_days(
    from_currency, to_currency, from_date, to_date
) -> int:
    """Count the number of days exisiting in an interval for a rated couple of currencies.

    Args:
        from_currency (str): The currency code for the base currency
        to_currency (str): The currency code for the target changed currency
        from_date (date): The start date of the interval
        to_date (date): The end date of the interval

    Returns:
        int: The number of existing consecutives days of rating for the pair currency A / currency B
    """
    return (
        CurrencyExchangeRate.objects.filter(
            source_currency__code=from_currency,
            exchanged_currency__code=to_currency,
            valuation_date__range=[from_date, to_date],
        )
        .select_related()
        .count()
    )


def exists_currency_rates_during_interval_for_pair_of_currencies(
    from_currency_code,
    to_currency_code,
    from_date: arrow.Arrow,
    to_date: arrow.Arrow,
) -> bool:
    """Indicate if it exists a couple of currencies rated for an interval of time.

    Args:
        from_currency_code (strt): The currency code for the base currency
        to_currency_code (str): The currency code for the target changed currency
        from_date (arrow.Arrow): an Arrow representing the start date of the interval
        to_date (arrow.Arrow): an Arrow representing the end date of the interval

    Returns:
        bool: True if the interval is filled by rates. False otherwise.
    """
    return get_number_of_consecutive_days(
        from_currency=from_currency_code,
        to_currency=to_currency_code,
        from_date=from_date.date(),
        to_date=to_date.date(),
    ) == len(list(arrow.Arrow.span_range("day", from_date, to_date)))
