"""Convert ADIF ADI content to dictionary and vice versa"""

import re
import datetime

__author_name__ = 'Andreas Schawo'
__author_email__ = 'andreas@schawo.de'
__copyright__ = 'Copyright 2023 by Andreas Schawo,licensed under CC BY-SA 4.0'
__proj_name__ = 'PyADIF-File'
__version__ = '0.1'
__description__ = 'Convert ADIF ADI content to dictionary and vice versa'


class TooMuchHeadersException(Exception):
    pass


class TagDefinitionException(Exception):
    pass


def unpack(data: str) -> dict:
    """Unpack header or record part to dictionary
    The parameters are converted to uppercase"""

    unpacked = {}

    start = -1
    end = 0
    length = 0

    while start < len(data):
        try:
            start = data.index('<', end + 1 + length)
        except ValueError:
            break

        end = data.index('>', start)
        tag = data[start + 1:end]
        try:
            param, length = tag.split(':')
        except ValueError:
            raise TagDefinitionException('Wrong param:length')

        try:
            length = int(length)
        except ValueError:
            raise TagDefinitionException('Wrong length')

        value = data[end + 1:end + 1 + length]
        unpacked[param.upper()] = value

    return unpacked


def adi2dict(adi: str) -> dict:
    """Turn ADI formated string to dictionary
    The parameters are converted to uppercase

        {
        'HEADER': None,
        'RECORDS': [list of records]
        }
    """

    doc = {'HEADER': None,
           'RECORDS': []
           }

    record_data = adi
    if not adi.startswith('<'):
        hr_list = re.split(r'<[eE][oO][hH]>', adi)
        if len(hr_list) > 2:
            raise TooMuchHeadersException()

        doc['HEADER'] = unpack(hr_list[0])
        record_data = hr_list[1]

    rec_list = re.split(r'<[eE][oO][rR]>', record_data)
    for rec in rec_list:
        if rec.strip():
            doc['RECORDS'].append(unpack(rec))

    return doc


def pack(param: str, value: str) -> str:
    """Generates ADI tag if value is not empty

    :param param: the tag parameter (converte to uppercase)
    :param value: the tag value
    :return: <param:length>value
    """

    return f'<{param.upper()}:{len(str(value))}>{value}' if value else ''


def dict2adi(data_dict: dict, comment: str = 'ADIF export by ' + __proj_name__) -> str:
    """Takes a dictionary and converts it to ADI format
    Parameters can be in upper or lower case. The output is upper case.
    User has to care that parameters are not doubled!

    If 'HEADER' is present the comment is added and missing header fields are filled with defaults."""

    default = {'ADIF_VER': '3.1.4',
               'PROGRAMID': __proj_name__,
               'PROGRAMVERSION': __version__,
               'CREATED_TIMESTAMP': datetime.datetime.utcnow().strftime('%Y%m%d %H%M%S')
               }

    data = ''

    if 'HEADER' in data_dict:
        data = comment + ' \n'

        for p in data_dict['HEADER']:
            if p.upper() in ('ADIF_VER', 'PROGRAMID', 'PROGRAMVERSION', 'CREATED_TIMESTAMP'):
                data += pack(p.upper(), data_dict['HEADER'][p]) + '\n'
                default.pop(p.upper())
        for p in default:
            data += pack(p, default[p]) + '\n'
        data += '<EOH>\n\n'

    if 'RECORDS' in data_dict:
        for r in data_dict['RECORDS']:
            for i, pv in enumerate(zip(r.keys(), r.values()), 1):
                data += pack(pv[0].upper(), pv[1]) + ('\n' if i % 5 == 0 else ' ')
            if not data.endswith('\n'):
                data += '\n'
            data += '<EOR>\n\n'

    return data.strip()
