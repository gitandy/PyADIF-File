# PyADIF-File (c) 2023-2025 by Andreas Schawo is licensed under CC BY-SA 4.0.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/

"""Convert ADIF ADI content to dictionary and vice versa"""

import os
import re
import copy
from collections.abc import Iterator

import xmltodict

from . import __version_str__, __proj_name__
from .util import get_cur_adif_dt


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


class IllegalFieldNameException(Exception):
    pass


REGEX_ASCII = re.compile(r'[ -~\n\r]*')
REGEX_PARAM = re.compile(r'[a-zA-Z][a-zA-Z_0-9]*')


def collect_adi_fields(adx_xsd_name: str) -> dict[str, list]:
    """Collect the ADI allowed fields from the ADX XSD-File"""

    allowed_header_fields = ()
    allowed_record_fields = ()

    with open(adx_xsd_name, encoding='utf-8') as xsd:
        xml_txt = xsd.read()
    xsd_dict = xmltodict.parse(xml_txt)

    def get_fields(e):
        for field in e['xs:complexType']['xs:choice']['xs:element']:
            if field['@name'] in ('USERDEF', 'APP') or field['@name'].endswith('_INTL'):
                continue
            yield field['@name']

    for element in xsd_dict['xs:schema']['xs:element']['xs:complexType']['xs:sequence']['xs:element']:
        if element['@name'] == 'HEADER':
            allowed_header_fields = list(get_fields(element))
        elif element['@name'] == 'RECORDS':
            allowed_record_fields = list(get_fields(element['xs:complexType']['xs:sequence']['xs:element']))
        else:
            continue

    return {'HEADER_FIELDS': allowed_header_fields,
            'RECORD_FIELDS': allowed_record_fields}


ALLOWED_FIELDS = collect_adi_fields(os.path.join(os.path.dirname(__file__), 'xsd/adx314.xsd'))


def validate_field(field: str, header: bool = False, value: str = '', userdefs=None):
    """validates a field name for compliance with ADIF definition and raise an exception otherwise

    :param field: the field name
    :param header: if a header field is to be validated
    :param value: the value for USERDEF validates
    :param userdefs: the list of user defined fields"""

    if userdefs is None:
        userdefs = []

    if header:
        if field.startswith('USERDEF') and value.upper() in ALLOWED_FIELDS['RECORD_FIELDS']:
            raise IllegalFieldNameException(f'User definition redefines standard field: {value}')

        if field not in ALLOWED_FIELDS['HEADER_FIELDS'] and not field.startswith('USERDEF'):
            raise IllegalFieldNameException(f'Header field: {field}')
    else:
        if field not in ALLOWED_FIELDS['RECORD_FIELDS'] and not field.startswith('APP_') and field not in userdefs:
            raise IllegalFieldNameException(f'Record field: {field}')


def unpack(data: str, validate: bool = False, header: bool = False, userdefs: list = None) -> dict[
    str, str | list[dict]]:
    """Unpack header or record part to dictionary
    The parameters are converted to uppercase

    :param data: the string to extract the ADIF fields from
    :param validate: if the fields to be validated to comply to the definition
    :param header: if it is the header to be unpacked
    :param userdefs: the list of user defined fields
    :return: a dict of field name value pairs"""

    if userdefs is None:
        userdefs = []

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
            param = tag_def[0].upper()
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
        if param.startswith('USERDEF'):
            if 'USERDEFS' not in unpacked:
                unpacked['USERDEFS'] = []
            unpacked['USERDEFS'].append({'dtype': dtype,
                                         'userdef': value.upper()})
        else:
            unpacked[param] = value

        if validate:
            validate_field(param, header, value, userdefs=userdefs)

    return unpacked


def loadi(adi: str, skip: int = 0, validate: bool = False) -> Iterator[dict[str, str]]:
    """Turn ADI formated string to header/records as an iterator over dict
    The skip option is useful if you want to watch a file for new records only. This saves processing time.

    :param adi: the ADI data
    :param skip: skip first number of records (does not apply for header)
    :param validate: if the fields to be validated to comply to the definition
    :return: an iterator of records (first record is the header even if not available)
    """

    userdefs = []
    hr_list = re.split(r'<[eE][oO][hH]>', adi)

    if len(hr_list) == 1:  # Header is missing
        yield {}
        record_data = hr_list[0]
    elif len(hr_list) > 2:  # More than one header
        raise TooMuchHeadersException()
    else:  # One header and the records
        data = unpack(hr_list[0], validate, True)
        if 'USERDEFS' in data:
            for ud in data['USERDEFS']:
                userdefs.append(ud['userdef'])
        yield data
        record_data = hr_list[1]

    for i, rec in enumerate(re.finditer(r'(.*?)<[eE][oO][rR]>', record_data, re.S)):
        if i >= skip:
            yield unpack(rec.groups()[0], validate, userdefs=userdefs)


def loads(adi: str, skip: int = 0, validate: bool = False) -> dict:
    """Turn ADI formated string to dictionary
    The parameters are converted to uppercase

        {
        'HEADER': {},
        'RECORDS': [list of records]
        }

    The skip option is useful if you want to watch a file for new records only. This saves processing time.
    In this case consider to use loadi() directly.

    :param adi: the ADI data
    :param skip: skip first number of records (does not apply for header)
    :param validate: if the fields to be validated to comply to the definition
    :return: the ADI as a dict
    """

    doc = {'HEADER': {},
           'RECORDS': []
           }

    first = True
    for rec in loadi(adi, skip, validate):
        if first:
            doc['HEADER'] = rec
            first = False
        else:
            doc['RECORDS'].append(rec)

    return doc


def load(file_name: str, skip: int = 0, validate: bool = False, encoding=None) -> dict:
    """Load ADI formated file to dictionary
       The parameters are converted to uppercase

           {
           'HEADER': {},
           'RECORDS': [list of records]
           }

       The skip option is useful if you want to watch a file for new records only. This saves processing time.
       In this case consider to use loadi() directly.

       :param file_name: the file name where the ADI data is stored
       :param skip: skip first number of records (does not apply for header)
       :param validate: if the fields to be validated to comply to the definition
       :param encoding: the file encoding
       :return: the ADI as a dict
       """

    with open(file_name, encoding=encoding) as af:
        data = af.read()

    return loads(data, skip, validate)


def pack(param: str, value: str, dtype: str = None, validate: bool = True, header: bool = False, userdefs=None) -> str:
    """Generates ADI tag if value is not empty
    Does not generate tags for *_INTL types as required by specification.

    :param param: the tag parameter (will be converted to uppercase)
    :param value: the tag value (or tag definition if param is a USERDEF field)
    :param dtype: the optional datatype (mainly used for USERDEFx in header)
    :param validate: if the fields to be validated to comply to the definition
    :param header: if a header field is to be validated
    :param userdefs: the list of user defined fields
    :return: <param:length>value
    """

    if userdefs is None:
        userdefs = []

    if not re.fullmatch(REGEX_PARAM, param):
        raise IllegalParameterException(f'Parameter "{param}" contains not allowed characters')

    if validate:
        validate_field(param.upper(), header, value=value, userdefs=userdefs)

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


def dumpi(data_dict: dict, comment: str = 'ADIF export by ' + __proj_name__, validate: bool = True,
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
    :param validate: if the fields to be validated to comply to the definition
    :param linebreaks: Format output with additional linebreaks for readability
    :param spaces: Number of spaces between fields
    :return: an iterator of chunks of the ADI (header, record 1, ..., record n)"""

    data_dict = copy.deepcopy(data_dict)

    field_separator = ' ' * spaces if spaces >= 0 else ' '

    userdefs = []
    if 'HEADER' in data_dict:
        default = {'ADIF_VER': '3.1.4',
                   'PROGRAMID': __proj_name__,
                   'PROGRAMVERSION': __version_str__,
                   'CREATED_TIMESTAMP': get_cur_adif_dt(),
                   }

        data = comment + ' \n'

        for p in data_dict['HEADER']:
            if p.upper() in ('ADIF_VER', 'PROGRAMID', 'PROGRAMVERSION', 'CREATED_TIMESTAMP'):
                data += (pack(p.upper(), data_dict['HEADER'][p], validate=validate, header=True) +
                         ('\n' if linebreaks else field_separator))
                default.pop(p.upper())
            elif p.upper() == 'USERDEFS':
                for i, u in enumerate(data_dict['HEADER'][p], 1):
                    userdefs.append(u['userdef'].upper())
                    data += (pack(f'USERDEF{i}', u['userdef'], u['dtype'], validate=validate, header=True) +
                             ('\n' if linebreaks else field_separator))
        for p in default:
            data += pack(p, default[p], validate=validate, header=True) + (
                '\n' if linebreaks else field_separator)
        data += '<EOH>'
        yield data

    if 'RECORDS' in data_dict:
        for r in data_dict['RECORDS']:
            data = ''
            empty = True
            for i, pv in enumerate(zip(r.keys(), r.values()), 1):
                tag = pack(pv[0].upper(), pv[1], validate=validate, userdefs=userdefs)
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


def dumps(data_dict: dict, comment: str = 'ADIF export by ' + __proj_name__, validate: bool = True,
          linebreaks: bool = True, **params) -> str:
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
    :param validate: if the fields to be validated to comply to the definition
    :param linebreaks: Format output with additional linebreaks for readability
    :return: the complete ADI as a string"""

    line_separator = '\n\n' if linebreaks else '\n'

    return line_separator.join(list(dumpi(data_dict, comment, validate, linebreaks=linebreaks, **params)))


def dump(file_name: str, data_dict: dict, comment: str = 'ADIF export by ' + __proj_name__,
         validate: bool = True, linebreaks: bool = True, encoding='ascii', **params):
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
    :param validate: if the fields to be validated to comply to the definition
    :param linebreaks: format output with additional linebreaks for readability
    :param encoding: the file encoding"""

    with open(file_name, 'w', encoding=encoding) as af:
        first = True
        for chunk in dumpi(data_dict, comment, validate, linebreaks=linebreaks, **params):
            if first:
                first = False
            else:
                af.write('\n\n' if linebreaks else '\n')
            af.write(chunk)


__all__ = ['load', 'loads', 'loadi', 'dump', 'dumps', 'dumpi',
           'TooMuchHeadersException', 'TagDefinitionException',
           'IllegalDataTypeException', 'IllegalParameterException',
           'StringNotASCIIException', 'IllegalFieldNameException']
