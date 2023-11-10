"""Convert ADIF ADI content to dictionary and vice versa"""

import re
import datetime
from collections.abc import Iterator

from adif_file.__version__ import __version__ as __version_str__

__author_name__ = 'Andreas Schawo'
__author_email__ = 'andreas@schawo.de'
__copyright__ = 'Copyright 2023 by Andreas Schawo,licensed under CC BY-SA 4.0'
__proj_name__ = 'PyADIF-File'
__version__ = __version_str__[1:].split('-')[0]
__description__ = 'Convert ADIF ADI content to dictionary and vice versa'


class TooMuchHeadersException(Exception):
    pass


class TagDefinitionException(Exception):
    pass


class StringNotASCIIException(Exception):
    pass


class IllegalParameterException(Exception):
    pass


class IllegalDataTypeException(Exception):
    pass


REGEX_ASCII = re.compile(r'[ -~\n\r]*')
REGEX_PARAM = re.compile(r'[a-zA-Z][a-zA-Z_0-9]*')


def unpack(data: str) -> dict:
    """Unpack header or record part to dictionary
    The parameters are converted to uppercase"""

    unpacked = {}

    start = -1
    end = -1
    length = 0

    while start < len(data):
        try:
            start = data.index('<', end + 1 + length)
        except ValueError:
            break

        end = data.index('>', start)
        tag = data[start + 1:end]
        dtype = None
        try:
            tag_def = tag.split(':')
            param = tag_def[0]
            length = tag_def[1]
            if len(tag_def) == 3:
                dtype = tag_def[2]
        except ValueError:
            raise TagDefinitionException('Wrong tag definition')

        try:
            length = int(length)
        except ValueError:
            raise TagDefinitionException('Wrong length')

        value = data[end + 1:end + 1 + length]
        if param.upper().startswith('USERDEF'):
            if 'USERDEFS' not in unpacked:
                unpacked['USERDEFS'] = []
            unpacked['USERDEFS'].append({'dtype': dtype,
                                         'userdef': value})
        else:
            unpacked[param.upper()] = value

    return unpacked


def loads_adi(adi: str) -> dict:
    """Turn ADI formated string to dictionary
    The parameters are converted to uppercase

        {
        'HEADER': None,
        'RECORDS': [list of records]
        }

    :param adi: the ADI data
    :return: the ADI as a dict
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


def load_adi(file_name: str):
    """Turn ADI formated string to dictionary
       The parameters are converted to uppercase

           {
           'HEADER': None,
           'RECORDS': [list of records]
           }

       :param file_name: the file name where the ADI data is stored
       :return: the ADI as a dict
       """

    with open(file_name, encoding='ascii') as af:
        data = af.read()

    return loads_adi(data)


def pack(param: str, value: str, dtype: str = None) -> str:
    """Generates ADI tag if value is not empty
    Does not generate tags for *_INTL types as required by specification.

    :param param: the tag parameter (converte to uppercase)
    :param value: the tag value (or tag definition if param is a USERDEF field)
    :param dtype: the optional datatype (mainly used for USERDEFx in header)
    :return: <param:length>value
    """

    if not re.fullmatch(REGEX_PARAM, param):
        raise IllegalParameterException(f'Parameter "{param}" contains not allowed characters')

    if not param.upper().endswith('_INTL'):
        if isinstance(value, str) and not re.fullmatch(REGEX_ASCII, value):
            raise StringNotASCIIException(f'Value "{value}" in parameter "{param}" contains non ASCII characters')

        if dtype:
            if len(dtype) > 1 or dtype not in 'BNDTSEL':
                raise IllegalDataTypeException(f'Datatype "{dtype}" in "{param}"')
            return f'<{param.upper()}:{len(str(value))}:{dtype}>{value}' if value else ''
        else:
            return f'<{param.upper()}:{len(str(value))}>{value}' if value else ''
    else:
        return ''


def dumpi_adi(data_dict: dict, comment: str = 'ADIF export by ' + __proj_name__) -> Iterator[str]:
    """Takes a dictionary and converts it to ADI format
    Parameters can be in upper or lower case. The output is upper case. The user must take care
    that parameters are not doubled!
    *_INTL parameters are ignored as they are not allowed in ADI.
    Empty records are skipped.

    If 'HEADER' is present the comment is added and missing header fields are filled with defaults.
    The header can contain a list of user definitions as USERDEFS. Each user definition is expected as a dictionary
    with datatype as "dtype" and field definition as "userdef" instead of a string value.

    :param data_dict: the dictionary with header and records
    :param comment: the comment to induce the header
    :return: an iterator of chunks of the ADI:"""

    default = {'ADIF_VER': '3.1.4',
               'PROGRAMID': __proj_name__,
               'PROGRAMVERSION': __version__,
               'CREATED_TIMESTAMP': datetime.datetime.utcnow().strftime('%Y%m%d %H%M%S')
               }

    if 'HEADER' in data_dict:
        data = comment + ' \n'

        for p in data_dict['HEADER']:
            if p.upper() in ('ADIF_VER', 'PROGRAMID', 'PROGRAMVERSION', 'CREATED_TIMESTAMP'):
                data += pack(p.upper(), data_dict['HEADER'][p]) + '\n'
                default.pop(p.upper())
            elif p.upper() == 'USERDEFS':
                for i, u in enumerate(data_dict['HEADER'][p], 1):
                    data += pack(f'USERDEF{i}', u['userdef'], u['dtype']) + '\n'
        for p in default.items():
            data += pack(p, default[p]) + '\n'
        data += '<EOH>'
        yield data

    if 'RECORDS' in data_dict:
        for r in data_dict['RECORDS']:
            data = ''
            empty = True
            for i, pv in enumerate(zip(r.keys(), r.values()), 1):
                tag = pack(pv[0].upper(), pv[1])
                if tag:
                    empty = False
                    data += tag + ('\n' if i % 5 == 0 else ' ')
            if not data.endswith('\n'):
                data += '\n'

            if not empty:
                data += '<EOR>'
                yield data


def dumps_adi(data_dict: dict, comment: str = 'ADIF export by ' + __proj_name__) -> str:
    """Takes a dictionary and converts it to ADI format
    Parameters can be in upper or lower case. The output is upper case. The user must take care
    that parameters are not doubled!
    *_INTL parameters are ignored as they are not allowed in ADI.
    Empty records are skipped.

    If 'HEADER' is present the comment is added and missing header fields are filled with defaults.
    The header can contain a list of user definitions as USERDEFS. Each user definition is expected as a dictionary
    with datatype as "dtype" and field definition as "userdef" instead of a string value.

    :param data_dict: the dictionary with header and records
    :param comment: the comment to induce the header
    :return: the complete ADI as a string"""

    return '\n\n'.join(list(dumpi_adi(data_dict, comment)))


def dump_adi(file_name: str, data_dict: dict, comment: str = 'ADIF export by ' + __proj_name__):
    """Takes a dictionary and stores it to filename in ADI format
    Parameters can be in upper or lower case. The output is upper case. The user must take care
    that parameters are not doubled!
    *_INTL parameters are ignored as they are not allowed in ADI.
    Empty records are skipped.

    If 'HEADER' is present the comment is added and missing header fields are filled with defaults.
    The header can contain a list of user definitions as USERDEFS. Each user definition is expected as a dictionary
    with datatype as "dtype" and field definition as "userdef" instead of a string value.

    :param file_name: the filename to store the ADI data to
    :param data_dict: the dictionary with header and records
    :param comment: the comment to induce the header
    :return: the complete ADI as a string"""

    with open(file_name, 'w', encoding='ascii') as af:
        first = True
        for chunk in dumpi_adi(data_dict, comment):
            if first:
                first = False
            else:
                af.write('\n\n')

            af.write(chunk)
