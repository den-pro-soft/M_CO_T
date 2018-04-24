"""Provides common validation logic"""

import re
from datetime import datetime


PAYE_REGEX = re.compile(r"^\d{3}/[A-Z0-9]{1,12}$")
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def check_posi_integer(errors, subject, label):
    """Checks if the subject is a positive integer"""
    try:
        number = int(subject)
        if number <= 0:
            errors.append('{0} should be a positive number'.format(label))
    except ValueError:
        errors.append('{0} should be a number'.format(label))


def check_paye_reference(errors, subject, label):
    """Checks if a PAYE reference is valid"""
    match = PAYE_REGEX.match(subject)
    if match is None:
        errors.append('{0} should be a valid PAYE Reference'.format(label))


def check_date(errors, subject, label):
    """Checks if a date is valid"""
    if subject is None:
        return None
    try:
        return datetime.strptime(subject, '%d/%m/%Y')
    except ValueError:
        pass
    try:
        return datetime.strptime(subject, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        pass
    try:
        return datetime.strptime(subject, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        pass
    try:
        return datetime.strptime(subject, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass
    try:
        return datetime.strptime(subject, '%Y-%m-%d')
    except ValueError:
        pass
    errors.append('{0} should be a valid date'.format(label))
    return None


def check_time(errors, subject, label):
    """Checks if a time value is valid"""
    if subject is None or subject == ':':
        return None
    try:
        return datetime.strptime(subject, '%H:%M').time()
    except ValueError:
        pass
    errors.append('{0} should be a valid time (e.g. 23:59)'.format(label))
    return None


def check_email(errors, subject, label):
    """Checks if an e-mail address is valid"""
    match = EMAIL_REGEX.match(subject)
    if match is None:
        errors.append('{0} should be a valid e-mail address'.format(label))
