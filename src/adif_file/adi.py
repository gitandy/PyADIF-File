"""Convert ADIF ADI content to dictionary and vice versa"""

import re
import copy
import datetime
from collections.abc import Iterator

from adif_file.__version__ import __version__ as __version_str__

__proj_name__ = 'PyADIF-File'
__version__ = __version_str__[1:].split('-')[0]


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


def loadi(adi: str, skip: int = 0) -> Iterator[dict]:
    """Turn ADI formated string to header/records as an iterator over dict
    The skip option is useful if you want to watch a file for new records only. This saves processing time.

    :param adi: the ADI data
    :param skip: skip first number of records (does not apply for header)
    :return: an iterator of records (first record is the header even if not available)
    """

    record_data = adi
    if not adi.startswith('<'):  # If a header is available
        hr_list = re.split(r'<[eE][oO][hH]>', adi)
        if len(hr_list) > 2:
            raise TooMuchHeadersException()

        yield unpack(hr_list[0])
        record_data = hr_list[1]
    else:  # Empty record for missing header
        yield {}

    i = 0
    for rec in re.finditer(r'(.*?)<[eE][oO][rR]>', record_data, re.S):
        if i >= skip:
            yield unpack(rec.groups()[0])
        i += 1


def loads(adi: str, skip: int = 0) -> dict:
    """Turn ADI formated string to dictionary
    The parameters are converted to uppercase

        {
        'HEADER': None,
        'RECORDS': [list of records]
        }

    The skip option is useful if you want to watch a file for new records only. This saves processing time.
    In this case consider to use loadi() directly.

    :param adi: the ADI data
    :param skip: skip first number of records (does not apply for header)
    :return: the ADI as a dict
    """

    doc = {'HEADER': None,
           'RECORDS': []
           }

    first = True
    for rec in loadi(adi, skip):
        if first:
            doc['HEADER'] = rec
            first = False
        else:
            doc['RECORDS'].append(rec)

    return doc


def load(file_name: str, skip: int = 0, encoding=None) -> dict:
    """Load ADI formated file to dictionary
       The parameters are converted to uppercase

           {
           'HEADER': None,
           'RECORDS': [list of records]
           }

       The skip option is useful if you want to watch a file for new records only. This saves processing time.
       In this case consider to use loadi() directly.

       :param file_name: the file name where the ADI data is stored
       :param skip: skip first number of records (does not apply for header)
       :param encoding: the file encoding
       :return: the ADI as a dict
       """

    with open(file_name, encoding=encoding) as af:
        data = af.read()

    return loads(data, skip)


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


def dumpi(data_dict: dict, comment: str = 'ADIF export by ' + __proj_name__,
          linebreaks: bool = True, spaces: int = 1) -> Iterator[str]:
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
    :param linebreaks: Format output with additional linebreaks for readability
    :param spaces: Number of spaces between fields
    :return: an iterator of chunks of the ADI (header, record 1, ..., record n)"""

    data_dict = copy.deepcopy(data_dict)

    field_separator = ' ' * spaces if spaces >= 0 else ' '

    if 'HEADER' in data_dict:
        default = {'ADIF_VER': '3.1.4',
                   'PROGRAMID': __proj_name__,
                   'PROGRAMVERSION': __version__,
                   'CREATED_TIMESTAMP': datetime.datetime.utcnow().strftime('%Y%m%d %H%M%S')
                   # TODO: Fix deprication > 3.10: datetime.datetime.now(tz=datetime.UTC).strftime('%Y%m%d %H%M%S')
                   }

        data = comment + ' \n'

        for p in data_dict['HEADER']:
            if p.upper() in ('ADIF_VER', 'PROGRAMID', 'PROGRAMVERSION', 'CREATED_TIMESTAMP'):
                data += pack(p.upper(), data_dict['HEADER'][p]) + ('\n' if linebreaks else field_separator)
                default.pop(p.upper())
            elif p.upper() == 'USERDEFS':
                for i, u in enumerate(data_dict['HEADER'][p], 1):
                    data += pack(f'USERDEF{i}', u['userdef'], u['dtype']) + ('\n' if linebreaks else field_separator)
        for p in default:
            data += pack(p, default[p]) + ('\n' if linebreaks else field_separator)
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
                    if linebreaks:
                        data += tag + ('\n' if i % 5 == 0 else field_separator)
                    else:
                        data += tag + field_separator
            if not data.endswith('\n'):
                data += '\n' if linebreaks else ''

            if not empty:
                data += '<EOR>'
                yield data


def dumps(data_dict: dict, comment: str = 'ADIF export by ' + __proj_name__, linebreaks: bool = True, **params) -> str:
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
    :param linebreaks: Format output with additional linebreaks for readability
    :return: the complete ADI as a string"""

    line_separator = '\n\n' if linebreaks else '\n'

    return line_separator.join(list(dumpi(data_dict, comment, linebreaks=linebreaks, **params)))


def dump(file_name: str, data_dict: dict, comment: str = 'ADIF export by ' + __proj_name__,
         linebreaks: bool = True, encoding='ascii', **params):
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
    :param linebreaks: format output with additional linebreaks for readability
    :param encoding: the file encoding"""

    with open(file_name, 'w', encoding=encoding) as af:
        first = True
        for chunk in dumpi(data_dict, comment, linebreaks=linebreaks, **params):
            if first:
                first = False
            else:
                af.write('\n\n' if linebreaks else '\n')

            af.write(chunk)


__all__ = ['load', 'loads', 'loadi', 'dump', 'dumps', 'dumpi',
           'TooMuchHeadersException', 'TagDefinitionException',
           'IllegalDataTypeException', 'IllegalParameterException',
           'StringNotASCIIException']
