"""Convert ADIF ADX content to dictionary and vice versa
The XML is validated against the XSD from ADIF.org"""

import datetime
import os.path
import xml
from xml.etree.ElementTree import ElementTree, ParseError

import xmlschema
import xmltodict

from adif_file.__version__ import __version__ as __version_str__

__proj_name__ = 'PyADIF-File'
__version__ = __version_str__[1:].split('-')[0]

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
        data_dict = xmltodict.parse(adx_data, cdata_key='$')
        data_dict = data_dict['ADX']
        if ('RECORDS' in data_dict and data_dict['RECORDS'] and
                'RECORD' in data_dict['RECORDS'] and data_dict['RECORDS']['RECORD']):
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


def dump(file_name: str, data_dict: dict):
    """Takes a dictionary and stores it to ADX xml file
       If 'HEADER' is missing the header fields are filled with defaults.
       The XML is validated against the strict XSD

       :param file_name: the filename to store the ADX data to
       :param data_dict: the dictionary with header and records
       """

    data_dict = data_dict.copy()

    header = {
        'ADIF_VER': '3.1.4',
        'PROGRAMID': __proj_name__,
        'PROGRAMVERSION': __version__,
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

    try:
        et = ADX_EXPORT_SCHEMA.encode(data_dict)
        ElementTree(et).write(file_name, xml_declaration=True, encoding='utf-8')
    except xmlschema.validators.exceptions.XMLSchemaChildrenValidationError as exc:
        raise UndefinedElementException(f'in {exc.elem.tag}') from None
    except xmlschema.validators.exceptions.XMLSchemaValidationError as exc:
        raise MalformedValueException(f'Field "{exc.elem.tag}": {exc.reason}') from None


__all__ = ['load', 'loads', 'dump', 'MissingRecordsException', 'UndefinedElementException',
           'MalformedValueException', 'XmlSyntaxError']
