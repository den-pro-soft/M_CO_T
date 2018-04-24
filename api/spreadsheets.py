"""Module for dealing with xlsx spreadsheets"""

import os
import io
from datetime import date, time, datetime
from openpyxl import load_workbook
import xlrd


def open_workbook_template(name):
    """Opens a workbook template"""
    module_dir = os.path.dirname(__file__)
    path = os.path.join(module_dir, 'templates', name)
    return load_workbook(path)


def remove_worksheet(book, sheet_name):
    """Removes a worksheet by name"""
    del book[sheet_name]


def get_bytes(book):
    """Gets a stream of bytes from a workbook"""
    stream = io.BytesIO()
    book.save(stream)
    stream.seek(0)
    return stream


def read_date(xlrdsheet, rowx, colx):
    """Reads a xldate from a xlrd worksheet as a datetime"""
    cell_value = xlrdsheet.cell_value(rowx=rowx, colx=colx)
    if not cell_value:
        return None
    elif isinstance(cell_value, str):
        return datetime.strptime(cell_value, '%d/%m/%Y')
    else:
        time_tuple = xlrd.xldate_as_tuple(cell_value, xlrdsheet.book.datemode)
        return date(*time_tuple[0:3])


def read_time(xlrdsheet, rowx, colx):
    """Reads a xldate from a xlrd worksheet as a time"""
    cell_value = xlrdsheet.cell_value(rowx=rowx, colx=colx)
    if cell_value is None or cell_value == '':
        return None
    elif isinstance(cell_value, str):
        try:
            return datetime.strptime(cell_value, '%H:%M')
        except ValueError:
            return datetime.strptime(cell_value, '%H%M')
    elif isinstance(cell_value, float):
        if cell_value < 1 and cell_value > 0:
            # time-formatted cell
            time_tuple = xlrd.xldate_as_tuple(cell_value, xlrdsheet.book.datemode)
            return time(*time_tuple[3:5])
        else:
            # 950 meaning 9:50
            return datetime.strptime(str(int(cell_value)).zfill(4), '%H%M')
    else:
        time_tuple = xlrd.xldate_as_tuple(cell_value, xlrdsheet.book.datemode)
        return time(*time_tuple[3:5])


def parse_text(value):
    """Parses a text value trying to workaround
    erroneous cell formats"""
    if isinstance(value, float):
        return str(int(value))
    return value
