"""This module provides a service for processing
raw employees. See PROCESSING.md for details"""

from models.employees import Employee


def process(raw_employees_data):
    """Process raw employees"""
    duplicated_ids = Employee.duplicated_ids(raw_employees_data)
    return [
        emp
        for emp in raw_employees_data
        if emp.effective_id not in duplicated_ids
        and emp.valid_work_arrangements()
    ]
