"""Convert ADIF ADX content to dictionary and vice versa
The XML is validated against the XSD from ADIF.org"""

import copy
import datetime
import os.path
import xml
from xml.etree.ElementTree import ElementTree, ParseError

import xmlschema
import xmltodict

from . import __version_str__, __proj_name__

ADX_EXPORT_SCHEMA = xmlschema.XMLSchema(os.path.join(os.path.dirname(__file__), 'xsd/adx314.xsd'))
ADX_IMPORT_SCHEMA = xmlschema.XMLSchema(os.path.join(os.path.dirname(__file__), 'xsd/adx314generic.xsd'))


class MissingRecordsException(Exception):
    pass


class UndefinedElementException(Exception):
    pass


class MalformedValueException(Exception):
    pass


class XmlSyntaxError(SyntaxError):
    pass


def loads(adx_data: str, validate: bool = False) -> dict:
    """Load ADX content to dictionary
       The ADX is not validated to conform to the standard

       :param adx_data: the ADX content
       :param validate: validate the ADX against the genereic XSD (very slow)
       :return: the ADX as a dict
       """

    if validate:
        try:
            ADX_IMPORT_SCHEMA.validate(adx_data)
        except ParseError as exc:
            raise XmlSyntaxError(str(exc)) from None
        except xmlschema.validators.exceptions.XMLSchemaChildrenValidationError as exc:
            raise UndefinedElementException(f'in {exc.elem.tag}') from None
        except xmlschema.validators.exceptions.XMLSchemaValidationError as exc:
            raise MalformedValueException(f'Field "{exc.elem.tag}": {exc.reason}') from None

    try:
        data_dict = xmltodict.parse(adx_data, cdata_key='$')['ADX']
        if all(('RECORDS' in data_dict, bool(data_dict['RECORDS']),
               'RECORD' in data_dict['RECORDS'], bool(data_dict['RECORDS']['RECORD']))):
            data_dict['RECORDS'] = data_dict['RECORDS']['RECORD']
        else:
            data_dict['RECORDS'] = []
        return data_dict
    except xml.parsers.expat.ExpatError as exc:
        raise XmlSyntaxError(str(exc)) from None


def load(file_name: str, validate: bool = False) -> dict:
    """Load ADX file to dictionary
       The XML is validated against the generic XSD

       :param file_name: the file name where the ADX data is stored
       :param validate: validate the ADX against the genereic XSD (very slow)
       :return: the ADX as a dict
       """

    with open(file_name, encoding='utf-8') as xf:
        adx_data = xf.read()

    return loads(adx_data, validate)


def dump(file_name: str, data_dict: dict, raise_exc=True) -> list[Exception]:
    """Takes a dictionary and stores it to ADX xml file
       If 'HEADER' is missing the header fields are filled with defaults.
       The XML is validated against the strict XSD

       :param file_name: the filename to store the ADX data to
       :param data_dict: the dictionary with header and records
       :param raise_exc: if the validation exceptions are to be raised immediately
       :return: list of validation exception (if not raised immediately)
       """

    data_dict = copy.deepcopy(data_dict)

    header = {
        'ADIF_VER': '3.1.4',
        'PROGRAMID': __proj_name__,
        'PROGRAMVERSION': __version_str__,
        'CREATED_TIMESTAMP': datetime.datetime.utcnow().strftime('%Y%m%d %H%M%S')
    }

    if 'HEADER' not in data_dict:
        data_dict['HEADER'] = header
    else:
        for h in header:
            if h not in data_dict['HEADER']:
                data_dict['HEADER'][h] = header[h]

    if 'RECORDS' not in data_dict:
        raise MissingRecordsException('Missing records in data_dict')

    rec = data_dict.pop('RECORDS')
    data_dict['RECORDS'] = {'RECORD': rec}

    exc = []

    et, errors = ADX_EXPORT_SCHEMA.encode(data_dict, validation='lax')
    for err in errors:
        if type(err) is xmlschema.validators.exceptions.XMLSchemaValidationError:
            if err.elem.tag == 'RECORD':
                exc.append(UndefinedElementException(f'{err.path}: {err.reason}'))
            elif err.elem.tag == 'HEADER':
                exc.append(UndefinedElementException(f'{err.path}: {err.reason}'))
            else:
                exc.append(MalformedValueException(f'{err.path}: value "{err.obj}" {err.reason}'))

    if raise_exc and exc:
        raise exc[0]

    ElementTree(et).write(file_name, xml_declaration=True, encoding='utf-8')
    return exc


__all__ = ['load', 'loads', 'dump', 'MissingRecordsException', 'UndefinedElementException',
           'MalformedValueException', 'XmlSyntaxError']
