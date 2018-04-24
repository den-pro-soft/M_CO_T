"""Utils for date manipulation"""

from datetime import datetime
from dateutil.relativedelta import relativedelta


def start_of_tax_year(subject):
    """Returns the start of the tax year given a date"""
    candidate = datetime(subject.year, 4, 6)
    if candidate > subject:
        return datetime(subject.year - 1, 4, 6)
    else:
        return candidate


def start_of_tax_month(subject):
    """Returns the start of the tax month given a date"""
    candidate = datetime(subject.year, subject.month, 6)
    if candidate > subject:
        return candidate - relativedelta(months=1)
    else:
        return candidate
