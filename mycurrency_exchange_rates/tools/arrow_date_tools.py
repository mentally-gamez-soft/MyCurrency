"""Control the correct format of a date passed to an arrow object."""

import arrow


def validate_arrow_date(year: int, month: int, day: int) -> dict:
    """Indicate if a date passed is correct.

    Args:
        year (int): the year
        month (int): the month
        day (int): the day

    Returns:
        dict: diotionary with a status [ok,ko], a message, a date created from an arrow
    """
    try:
        arrow_date = arrow.Arrow(year, month, day).date()
    except:
        return {
            "status": "ko",
            "mesage": "The valuation date is incorrect !",
        }

    return {"status": "ok", "arrow_date": arrow_date}
