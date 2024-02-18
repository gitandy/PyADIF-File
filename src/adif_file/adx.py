"""Convert ADIF ADX content to dictionary and vice versa
The XML is validated against the XSD from ADIF.org"""

import datetime
import os.path
from xml.etree.ElementTree import ElementTree, ParseError

import xmlschema

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


def load(file_name: str) -> dict:
    """Load ADX file to dictionary
       The XML is validated against the generic XSD

       :param file_name: the file name where the ADX data is stored
       :return: the ADX as a dict
       """

    try:
        data_dict = ADX_IMPORT_SCHEMA.to_dict(file_name, decimal_type=str)

        # Flatten records
        records = []
        for rec in data_dict['RECORDS']['RECORD']:
            for elem in rec:
                if type(rec[elem][0]) is str:  # Only for str to save APP data
                    rec[elem] = rec[elem][0]
            records.append(rec)
        data_dict['RECORDS'] = records

        # Flatten header
        header = {}
        for elem in data_dict['HEADER']:
            if type(data_dict['HEADER'][elem][0]) is str:  # Only for str to save USERDEF
                header[elem] = data_dict['HEADER'][elem][0]
        data_dict['HEADER'] = header
    except ParseError as exc:
        raise XmlSyntaxError(str(exc)) from None
    except xmlschema.validators.exceptions.XMLSchemaChildrenValidationError as exc:
        raise UndefinedElementException(f'in {exc.elem.tag}') from None
    except xmlschema.validators.exceptions.XMLSchemaValidationError as exc:
        raise MalformedValueException(f'Field "{exc.elem.tag}": {exc.reason}') from None

    return data_dict


def dump(file_name: str, data_dict: dict):
    """Takes a dictionary and stores it to ADX xml file
       If 'HEADER' is missing the header fields are filled with defaults.
       The XML is validated against the strict XSD

       :param file_name: the filename to store the ADX data to
       :param data_dict: the dictionary with header and records
       """

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


__all__ = ['load', 'dump', 'MissingRecordsException', 'UndefinedElementException',
           'MalformedValueException', 'XmlSyntaxError']
