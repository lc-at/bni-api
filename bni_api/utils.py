import datetime

from . import constants


def str_to_date(s: str) -> datetime.datetime:
    """Convert `str` to `datetime.datetime` object. Date format used
    here is corresponding to the correct format used in BNI's
    internet banking.
    """
    return datetime.datetime.strptime(s, constants.DATE_FORMAT)


def date_to_str(d: datetime.datetime) -> str:
    """Convert `datetime.datetime` to `str` object. Date format used
    here is corresponding to the correct format used in BNI's
    internet banking.
    """
    return datetime.datetime.strftime(d, constants.DATE_FORMAT)


def curr_to_int(curr: str) -> int:
    """Convert a currency formatted `str` to a regular `int`.
    This function currently supports only `<currency> <amount>,00`
    and '<amount>,00' format.
    Conversion of string 'IDR 30.000,00' will return `30000`
    """
    curr = curr.split().pop()
    for r in [',', '.', ' ']:
        curr = curr.replace(r, '')
    return int(curr[:len(curr)-2])
