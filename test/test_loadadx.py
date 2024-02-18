import os
import unittest

import adif_file.adx


def get_file_path(file):
    return os.path.join(os.path.dirname(__file__), file)


class LoadADX(unittest.TestCase):
    def test_10_goodfile(self):
        adx_exp_dict = {
            'HEADER': {'ADIF_VER': '3.1.4',
                       'CREATED_TIMESTAMP': '20231204 100000',
                       'PROGRAMID': 'PyADIF-File',
                       'PROGRAMVERSION': '1'},
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

        self.assertDictEqual(adx_exp_dict, adif_file.adx.load(get_file_path('testdata/goodfile.adx')))

    def test_20_badfile(self):
        self.assertRaises(adif_file.adx.XmlSyntaxError, adif_file.adx.load,
                          get_file_path('testdata/goodfile.txt'))

    def test_20_badxml(self):
        self.assertRaises(adif_file.adx.MalformedValueException, adif_file.adx.load,
                          get_file_path('testdata/badfile1.adx'))
        self.assertRaises(adif_file.adx.UndefinedElementException, adif_file.adx.load,
                          get_file_path('testdata/badfile2.adx'))


if __name__ == '__main__':
    unittest.main()
