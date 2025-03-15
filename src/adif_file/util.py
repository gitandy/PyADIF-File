# PyADIF-File (c) 2023-2025 by Andreas Schawo is licensed under CC BY-SA 4.0.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/

"""Provides some useful function to handle ADIF data"""

import sys
import datetime


def get_cur_adif_dt() -> str:
    """Get current date/time in ADIF format independant of Python version"""
    if sys.version_info[0] == 3 and sys.version_info[1] < 11:
        return datetime.datetime.utcnow().strftime('%Y%m%d %H%M%S')

    return datetime.datetime.now(datetime.UTC).strftime('%Y%m%d %H%M%S')


def adif_date2iso(date: str) -> str:
    """Tries to convert ADIF date to iso format"""
    if not date or len(date) != 8:
        return date
    return date[:4] + '-' + date[4:6] + '-' + date[6:8]


def adif_time2iso(time: str) -> str:
    """Tries to convert ADIF time to iso format"""
    if not time or len(time) not in (4, 6):
        return time
    return time[:2] + ':' + time[2:4] + (':' + time[4:6] if len(time) == 6 else '')


__all__ = ['get_cur_adif_dt', 'adif_date2iso', 'adif_time2iso']
