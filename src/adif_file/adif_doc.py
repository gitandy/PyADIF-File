# PyADIF-File (c) 2023-2025 by Andreas Schawo is licensed under CC BY-SA 4.0.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/

"""Provides an high level access to ADIF data"""
import os
from warnings import warn
from typing import Iterator, Union

from . import __version_str__, __proj_name__
from .util import get_cur_adif_dt, adif_time2iso, adif_date2iso
from . import adi, adx, util


class FormatWarning(Warning):
    pass


class ADIFRecordBase:
    """Base class for records like data abstraction"""
    __cls_fields__ = ()

    def __init__(self):
        self.__data__: dict[str, str] = {}

    def __str__(self):
        f = [f"{f}='{getattr(self, f)}'" for f in self.__cls_fields__]
        return f'{self.__class__.__name__}: {", ".join(f)}'

    @classmethod
    def from_dict(cls, rec: dict[str, str]) -> 'ADIFRecordBase':
        """Instantiate record object from a dictionary containing ADIF keys
        :param rec: the data mapping ADIF keys to values
        :return: record instance"""
        inst = cls()
        for k in rec:
            inst.__data__[k.upper()] = rec.get(k, '')
        return inst

    def to_dict(self) -> dict[str, str]:
        """Return the object data as dict with ADIF keys"""
        return self.__data__


class ADIFRecord(ADIFRecordBase):
    """Abstarction of ADIF QSO records"""
    __cls_fields__ = ('date', 'time', 'call', 'name', 'own_call')

    def __init__(self, date: str, time: str, own_call: str, call: str, band: str, mode: str,
                 rst_sent='', rst_rcvd='',
                 locator='', qth='', name='',
                 own_locator='', own_qth='', own_name=''):
        super().__init__()

        self.__data__ = {
            'QSO_DATE': util.iso_date2adif(date) if date else '',
            'TIME_ON': util.iso_time2adif(time) if time else '',
            'CALL': '',
            'NAME': '',
            'QTH': '',
            'GRIDSQUARE': '',
            'RST_SENT': '',
            'RST_RCVD': '',
            'BAND': '',
            'MODE': '',
            'FREQ': '',
            'TX_PWR': '',
            'STATION_CALLSIGN': '',
            'MY_NAME': '',
            'MY_CITY': '',
            'MY_GRIDSQUARE': '',
        }

        self.call = call
        self.own_call = own_call
        self.rst_sent = rst_sent if rst_sent else '599' if mode == 'CW' else '59'
        self.rst_rcvd = rst_rcvd if rst_rcvd else '599' if mode == 'CW' else '59'

    @property
    def date(self) -> str:
        return adif_date2iso(self.__data__['QSO_DATE'])

    @date.setter
    def date(self, date: str = ''):
        self.__data__['QSO_DATE'] = get_cur_adif_dt().split()[0] if not date else date.replace('-', '')

    @property
    def time(self) -> str:
        return adif_time2iso(self.__data__['TIME_ON'])

    @time.setter
    def time(self, time: str):
        self.__data__['TIME_ON'] = get_cur_adif_dt().split()[1] if not time else time.replace(':', '')

    @property
    def own_call(self) -> str:
        return self.__data__['STATION_CALLSIGN']

    @own_call.setter
    def own_call(self, callsign: str):
        if not util.check_format(util.REGEX_CALL, callsign):
            warn(f'Invalid callsign format "{callsign}"', FormatWarning)
        self.__data__['STATION_CALLSIGN'] = callsign

    @property
    def call(self) -> str:
        return self.__data__['CALL']

    @call.setter
    def call(self, callsign: str):
        if not util.check_format(util.REGEX_CALL, callsign):
            warn(f'Invalid callsign format "{callsign}"', FormatWarning)
        self.__data__['CALL'] = callsign

    @property
    def rst_sent(self) -> str:
        return self.__data__['RST_SENT']

    @rst_sent.setter
    def rst_sent(self, rst: str):
        if not util.check_format(util.REGEX_RST, rst):
            warn(f'Invalid RST format "{rst}"', FormatWarning)
        self.__data__['RST_SENT'] = rst

    @property
    def rst_rcvd(self) -> str:
        return self.__data__['RST_RCVD']

    @rst_rcvd.setter
    def rst_rcvd(self, rst: str):
        if not util.check_format(util.REGEX_RST, rst):
            warn(f'Invalid RST format "{rst}"', FormatWarning)
        self.__data__['RST_RCVD'] = rst

    @property
    def name(self) -> str:
        return self.__data__['NAME']


class ADIFHeader(ADIFRecordBase):
    """Abstarction of ADIF file header"""
    __cls_fields__ = ('adif_version', 'program_version', 'program_id', 'created')

    def __init__(self, adif_version: str = '3.1.4', program_id: str = __proj_name__,
                 program_version: str = __version_str__,
                 created: str = '', comment: str = 'ADIF export by ' + __proj_name__):
        super().__init__()
        self.__data__: dict[str, str] = {
            'ADIF_VER': adif_version,
            'PROGRAMID': program_id,
            'PROGRAMVERSION': program_version,
            'CREATED_TIMESTAMP': created if created else get_cur_adif_dt(),
        }
        self.__comment__ = comment

    @property
    def comment(self) -> str:
        return self.__comment__

    @property
    def adif_version(self) -> str:
        return self.__data__['ADIF_VER']

    @property
    def program_version(self) -> str:
        return self.__data__['PROGRAMVERSION']

    @property
    def program_id(self) -> str:
        return self.__data__['PROGRAMID']

    @property
    def created(self) -> str:
        try:
            date, time = self.__data__['CREATED_TIMESTAMP'].split(' ')
            return adif_date2iso(date) + ' ' + adif_time2iso(time)
        except ValueError:
            return ''


class ADIFDoc:
    """Abstraction of a whole ADIF file containing a header and multiple records"""

    def __init__(self, file_name=None,
                 own_call: str = '', own_locator: str = '', own_qth: str = '', own_name: str = ''):
        self.__records__: list[ADIFRecord] = []

        if file_name:
            if os.path.splitext(file_name)[-1] == '.adx':
                doc = adx.load(file_name)
            else:
                doc = adi.load(file_name)
            self.__header__ = ADIFHeader.from_dict(doc['HEADER'])
            for r in doc['RECORDS']:
                self.__records__.append(ADIFRecord.from_dict(r))
        else:
            self.__own_data__ = {
                'STATION_CALLSIGN': '',
                'MY_CITY': '',
                'MY_GRIDSQUARE': '',
                'MY_NAME': '',
            }

            self.__header__: ADIFHeader = ADIFHeader()
            self.__records__: list[ADIFRecord] = []

    @property
    def header(self) -> ADIFHeader:
        return self.__header__

    @header.setter
    def header(self, header: ADIFHeader):
        if type(header) is ADIFHeader:
            self.__header__ = header
        else:
            raise Exception('Header must be of type ADIFHeader')

    def create_record(self, date: str, time: str, own_call: str, call: str, band: str, mode: str,
                      **params) -> ADIFRecord:
        """Creates a new record, appends it to the list and also returns it
        If you gave your own data at class creation this data will be used"""
        params = self.__own_data__ | params
        rec = ADIFRecord(date, time, own_call, call, band, mode, **params)
        self.append_record(rec)
        return rec

    def append_record(self, rec: ADIFRecord):
        if type(rec) is ADIFRecord:
            self.__records__.append(rec)
        else:
            raise Exception('Record must be of type ADIFRecord')

    def records(self) -> Iterator[ADIFRecord]:
        yield from self.__records__

    def to_dict(self) -> dict[str, Union[dict[str, str], list[dict[str, str]]]]:
        doc = {
            'HEADER': self.__header__.to_dict(),
            'RECORDS': [r.to_dict() for r in self.__records__],
        }
        return doc

    def to_adx(self, file_name: str):
        adx.dump(file_name, self.to_dict())

    def to_adi(self, file_name: str = '') -> Union[str, None]:
        if file_name:
            adi.dump(file_name, self.to_dict(), self.__header__.comment)
            return None
        else:
            return adi.dumps(self.to_dict(), self.__header__.comment)

    def __str__(self):
        return f"{self.__class__.__name__}:{str(self.__header__).split(':', 1)[1]}, records={len(self.__records__)}"


__all__ = [ADIFDoc, ADIFRecord, ADIFHeader]
