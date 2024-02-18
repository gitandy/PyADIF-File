import os
import unittest

import adif_file.adx


def get_file_path(file):
    return os.path.join(os.path.dirname(__file__), file)


class DumpADX(unittest.TestCase):
    def test_10_dump_exceptions(self):
        adx_dict = {
            'RECORDS': [{'CALL': 'XX1XXX',
                         'QSO_DATE': '20231204',
                         'TIME_ON': '1100',
                         'QTH': 'Test'}]
        }

        self.assertRaises(adif_file.adx.MissingRecordsException, adif_file.adx.dump, '', {})

        adx_dict2 = adx_dict.copy()
        adx_dict2['RECORDS'][0]['MY_QTH'] = 'Test'  # MY_QTH is not allowed (MY_CITY)
        self.assertRaises(adif_file.adx.UndefinedElementException, adif_file.adx.dump, '', adx_dict2)

        adx_dict2 = adx_dict.copy()
        adx_dict2['RECORDS'][0]['MY_CITY'] = 123
        self.assertRaises(adif_file.adx.MalformedValueException, adif_file.adx.dump, '', adx_dict2)

        adx_dict2 = adx_dict.copy()
        adx_dict2['RECORDS'][0]['QTH'] = 'Töst'  # QTH ony alows ASCII chars < 127
        self.assertRaises(adif_file.adx.MalformedValueException, adif_file.adx.dump, '', adx_dict2)

        adx_dict2 = adx_dict.copy()
        adx_dict2['RECORDS'][0]['FREQ'] = 'Test'
        self.assertRaises(adif_file.adx.MalformedValueException, adif_file.adx.dump, '', adx_dict2)

    def test_20_dump(self):
        adx_dict = {
            'HEADER': {'PROGRAMVERSION': '1',
                       'CREATED_TIMESTAMP': '20231204 100000',
                       },
            'RECORDS': [{'CALL': 'XX1XXX',
                         'QSO_DATE': '20231204',
                         'TIME_ON': '1100',
                         'QTH': 'Test'
                         },
                        {'CALL': 'YY1YYY',
                         'QSO_DATE': '20231204',
                         'TIME_ON': '1200',
                         'QTH_INTL': 'Töst'
                         }]
        }

        adx_expected = '''<?xml version='1.0' encoding='utf-8'?>
<ADX>
    <HEADER>
        <PROGRAMVERSION>1</PROGRAMVERSION>
        <CREATED_TIMESTAMP>20231204 100000</CREATED_TIMESTAMP>
        <ADIF_VER>3.1.4</ADIF_VER>
        <PROGRAMID>PyADIF-File</PROGRAMID>
    </HEADER>
    <RECORDS>
        <RECORD>
            <CALL>XX1XXX</CALL>
            <QSO_DATE>20231204</QSO_DATE>
            <TIME_ON>1100</TIME_ON>
            <QTH>Test</QTH>
        </RECORD>
        <RECORD>
            <CALL>YY1YYY</CALL>
            <QSO_DATE>20231204</QSO_DATE>
            <TIME_ON>1200</TIME_ON>
            <QTH_INTL>Töst</QTH_INTL>
        </RECORD>
    </RECORDS>
</ADX>
'''

        temp_file = get_file_path('testdata/~test.adx')
        adif_file.adx.dump(temp_file, adx_dict)

        with open(temp_file, encoding='utf-8') as af:
            self.assertEqual(adx_expected, af.read())

        os.remove(temp_file)


if __name__ == '__main__':
    unittest.main()
