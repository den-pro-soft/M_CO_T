"""This module provides a service for calculating
report results. See PROCESSING.md for details"""

from itertools import groupby
from collections import defaultdict
from dateutil.relativedelta import relativedelta


ONE_DAY = relativedelta(days=1)


def process(employee_travel_history, from_date, to_date, categories):
    """Calculates report results"""

    employee_last_seem = defaultdict(lambda: from_date - ONE_DAY)
    employees = []

    intersecting_events = []
    for entry in employee_travel_history:
        last_seem = employee_last_seem[(entry['traveller_name'], entry['employee_id'])]
        applicable_to_date = not entry['to_date'] or entry['to_date'].date() > last_seem
        if entry['from_date'].date() <= to_date and applicable_to_date:
            intersecting_events.append(entry)

    history_grouped_by_employee = groupby(intersecting_events,
                                          lambda x: (x['traveller_name'], x['employee_id']))

    for employee_key, history in history_grouped_by_employee:
        stays = []
        filtered_history = filter(lambda x: x['category'] in categories, history)
        history_grouped_by_category = groupby(filtered_history, lambda x: x['category'])
        for category, entries in history_grouped_by_category:
            days = 0
            for entry in sorted(entries, key=lambda x: x['from_date']):
                entry_from_date = entry['from_date'].date()
                entry_to_date = entry['to_date'].date() if entry['to_date'] else None
                last_seem = employee_last_seem[employee_key]
                from_date_to_consider = max(last_seem + ONE_DAY, entry_from_date) \
                                        if entry_from_date else last_seem + ONE_DAY
                to_date_to_consider = min(to_date, entry_to_date) \
                                    if entry_to_date else to_date
                if to_date_to_consider >= from_date_to_consider:
                    difference = to_date_to_consider - from_date_to_consider
                    days += difference.days + 1
                    employee_last_seem[employee_key] = to_date_to_consider
            if days:
                stays.append({'category': category, 'days': days})
        if stays:
            employees.append({'traveller_name': employee_key[0],
                              'employee_id': employee_key[1],
                              'stays': stays})

    return employees
