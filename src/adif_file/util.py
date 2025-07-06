# PyADIF-File (c) 2023-2025 by Andreas Schawo is licensed under CC BY-SA 4.0.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/

"""Provides some useful function to handle ADIF data"""
import re
import sys
import datetime


def get_cur_adif_dt() -> str:
    """Get current date/time in ADIF format independant of Python version"""
    if sys.version_info[0] == 3 and sys.version_info[1] < 11:
        return datetime.datetime.utcnow().strftime('%Y%m%d %H%M%S')

    return datetime.datetime.now(datetime.UTC).strftime('%Y%m%d %H%M%S')


def adif_date2iso(date: str) -> str:
    """Tries to convert ADIF date to iso format"""
    if not check_format(REGEX_ADIFDATE, date):
        raise ValueError(f'Not a valide ADIF date "{date}"')
    return date[:4] + '-' + date[4:6] + '-' + date[6:8]


def adif_time2iso(time: str) -> str:
    """Tries to convert ADIF time to iso format"""
    if not check_format(REGEX_ADIFTIME, time):
        raise ValueError(f'Not a valide ADIF time "{time}"')
    return time[:2] + ':' + time[2:4] + (':' + time[4:6] if len(time) == 6 else '')


def iso_date2adif(date: str) -> str:
    """Converts an ISO formated date to ADIF"""
    if not check_format(REGEX_ISODATE, date):
        raise ValueError(f'Not a valide ISO date "{date}"')
    return date.replace('-', '')


def iso_time2adif(time: str) -> str:
    """Converts an ISO formated time to ADIF"""
    if not check_format(REGEX_ISOTIME, time):
        raise ValueError(f'Not a valide ISO time "{time}"')
    return time.replace(':', '')


REGEX_CALL = re.compile(r'([a-zA-Z0-9]{1,3}?/)?([a-zA-Z0-9]{1,3}?[0-9][a-zA-Z0-9]{0,3}?[a-zA-Z])(/[aAmMpPrRtT]{1,2}?)?')
REGEX_RST = re.compile(r'([1-5]([1-9]([1-9][aAcCkKmMsSxX]?)?)?)|([-+][0-9]{1,2})')
REGEX_LOCATOR = re.compile(r'[a-rA-R]{2}[0-9]{2}([a-xA-X]{2}([0-9]{2})?)?')
REGEX_NONASCII = re.compile(r'[ -~\n\r]*(.)?')
REGEX_ADIFTIME = re.compile(r'(([0-1][0-9])|(2[0-3]))([0-5][0-9])([0-5][0-9])?')
REGEX_ADIFDATE = re.compile(r'([1-9][0-9]{3})((0[1-9])|(1[0-2]))((0[1-9])|([1-2][0-9])|(3[0-1]))')
REGEX_ISOTIME = re.compile(r'(([0-1][0-9])|(2[0-3])):([0-5][0-9])(:[0-5][0-9])?')
REGEX_ISODATE = re.compile(r'([1-9][0-9]{3})-((0[1-9])|(1[0-2]))-((0[1-9])|([1-2][0-9])|(3[0-1]))')
# noinspection RegExpRedundantEscape
REGEX_EMAIL = re.compile(r'[\w\-\.]+@([\w-]+\.)+[\w-]{2,}')


def check_format(exp: re.Pattern, txt: str) -> bool:
    """Test the given text against a regular expression
    :param exp: a compiled pattern (e.g. util.REGEX_*)
    :param txt: a text
    :return: true if pattern matches"""
    return bool(re.fullmatch(exp, txt))


def check_call(call: str) -> None | tuple:
    """Test a call sign against a regular expression
    :param call: a call sign
    :return: tuple of parts ('Country prefix/', 'Call sign', '/Operation suffix')"""
    m = re.fullmatch(REGEX_CALL, call)
    if m:
        return m.groups()
    return None


def find_non_ascii(text: str) -> set:
    """Find all non ASCII chars in a text
    :param text: the text to search in
    :return: a set of non ASCII chars"""
    non_ascii = []
    for c in re.findall(REGEX_NONASCII, text):
        if c:
            non_ascii.append(c)
    return set(non_ascii)


def replace_non_ascii(text: str, replace: dict[str, str] = None, default: str = '_') -> str:
    """Replaces every non ASCII char with a str from a mapping
    :param text: the text containing non ASCII chars
    :param replace: a mapping with non ASCII chars and suiting substitutes (e.g. {'ä':'ae', 'ß':'ss'})
    :param default: the default substitute if no mapping is found
    :return: text with substitutes"""
    replace = replace if type(replace) is dict else {}
    default = default if type(default) is str else '_'
    for na in find_non_ascii(text):
        text = text.replace(na, replace.get(na, default))
    return text


__all__ = ['get_cur_adif_dt', 'adif_date2iso', 'adif_time2iso', 'iso_date2adif', 'iso_time2adif',
           'check_format', 'check_call', 'replace_non_ascii',
           'REGEX_ADIFDATE', 'REGEX_ADIFTIME', 'REGEX_ISODATE', 'REGEX_ISOTIME',
           'REGEX_EMAIL', 'REGEX_RST', 'REGEX_LOCATOR', 'REGEX_CALL']
