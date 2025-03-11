import os
import unittest

import adif_file.adi


def get_file_path(file: str):
    return os.path.join(os.path.dirname(__file__), file)


class LoadADI(unittest.TestCase):
    def test_10_unpack_header(self):
        adi_hdr1 = '''ADIF Export by Testprog
<ADIF_VER:5>3.1.4 <PROGRAMID:8>Testprog <PROGRAMVERSION:4>v0.2'''
        adi_hdr2 = '''ADIF Export by Testprog
    <ADIF_VER:5>3.1.4
    <PROGRAMID:8>Testprog 
    <PROGRAMVERSION:4>v0.2'''
        exp_dict = {'ADIF_VER': '3.1.4', 'PROGRAMID': 'Testprog', 'PROGRAMVERSION': 'v0.2'}

        self.assertDictEqual(exp_dict, adif_file.adi.unpack(adi_hdr1))
        self.assertDictEqual(exp_dict, adif_file.adi.unpack(adi_hdr2))

    def test_15_unpack_userdef(self):
        adi_hdr1 = '''ADIF Export by Testprog
<ADIF_VER:5>3.1.4 <PROGRAMID:8>Testprog <PROGRAMVERSION:4>v0.2 <USERDEF1:4:N>Test'''
        adi_hdr2 = '''ADIF Export by Testprog
<ADIF_VER:5>3.1.4hh <PROGRAMID:8>Testprog <PROGRAMVERSION:4>v0.2 <USERDEF1:4:G>Test <USERDEF2:5:L>TestX'''

        exp_dict1 = {'ADIF_VER': '3.1.4', 'PROGRAMID': 'Testprog', 'PROGRAMVERSION': 'v0.2',
                     'USERDEFS': [{'dtype': 'N',
                                   'userdef': 'Test'}]}
        exp_dict2 = {'ADIF_VER': '3.1.4', 'PROGRAMID': 'Testprog', 'PROGRAMVERSION': 'v0.2',
                     'USERDEFS': [{'dtype': 'G',
                                   'userdef': 'Test'},
                                  {'dtype': 'L',
                                   'userdef': 'TestX'}]}

        self.assertDictEqual(exp_dict1, adif_file.adi.unpack(adi_hdr1))
        self.assertDictEqual(exp_dict2, adif_file.adi.unpack(adi_hdr2))

    def test_20_unpack_record(self):
        adi_rec_app = '<APP_TESTAPP_CHANNEL:2:N>24'
        adi_rec_name = '<NAME:4>Test'

        self.assertDictEqual({'APP_TESTAPP_CHANNEL': '24'}, adif_file.adi.unpack(adi_rec_app))
        self.assertDictEqual({'NAME': 'Test'}, adif_file.adi.unpack(adi_rec_name))

    def test_50_goodfile(self):
        adi_dict = adif_file.adi.load(get_file_path('testdata/goodfile.txt'))

        self.assertIn('HEADER', adi_dict)
        self.assertIn('RECORDS', adi_dict)
        self.assertEqual(3, len(adi_dict['HEADER']))
        self.assertEqual(5, len(adi_dict['RECORDS']))

    def test_51_goodfile_missing_comment(self):
        adi_dict = adif_file.adi.load(get_file_path('testdata/goodfile_missing hcomment.txt'))

        self.assertIn('HEADER', adi_dict)
        self.assertIn('RECORDS', adi_dict)
        self.assertEqual(3, len(adi_dict['HEADER']))
        self.assertEqual(3, len(adi_dict['RECORDS']))

    def test_52_no_header(self):
        adi_dict = adif_file.adi.load(get_file_path('testdata/goodfile_no_h.txt'))

        self.assertIn('HEADER', adi_dict)
        self.assertIn('RECORDS', adi_dict)
        self.assertEqual(0, len(adi_dict['HEADER']))
        self.assertEqual(5, len(adi_dict['RECORDS']))

    def test_55_toomuchheaders(self):
        self.assertRaises(adif_file.adi.TooMuchHeadersException, adif_file.adi.load,
                          get_file_path('testdata/toomuchheadersfile.txt'))

    def test_60_skiprecords(self):
        adi_dict = adif_file.adi.load(get_file_path('testdata/goodfile.txt'), 3)
        rec_dict = {'QSO_DATE': '20231008', 'TIME_ON': '1754', 'RST_SENT': '59',
                    'RST_RCVD': '59', 'BAND': '2190M', 'MODE': 'AM', 'FREQ': '0.137',
                    'TX_PWR': '4.0', 'STATION_CALLSIGN': 'XX1XXX', 'MY_GRIDSQUARE': 'JO35uj27'}

        self.assertIn('HEADER', adi_dict)
        self.assertIn('RECORDS', adi_dict)
        self.assertEqual(3, len(adi_dict['HEADER']))
        self.assertEqual(2, len(adi_dict['RECORDS']))
        self.assertDictEqual(rec_dict, adi_dict['RECORDS'][0])

    def test_65_skiprec_noh(self):
        adi_dict = adif_file.adi.load(get_file_path('testdata/goodfile_no_h.txt'), 3)
        rec_dict = {'QSO_DATE': '20231008', 'TIME_ON': '1754', 'RST_SENT': '59',
                    'RST_RCVD': '59', 'BAND': '2190M', 'MODE': 'AM', 'FREQ': '0.137',
                    'TX_PWR': '4.0', 'STATION_CALLSIGN': 'XX1XXX', 'MY_GRIDSQUARE': 'JO35uj27'}

        self.assertIn('HEADER', adi_dict)
        self.assertIn('RECORDS', adi_dict)
        self.assertEqual(0, len(adi_dict['HEADER']))
        self.assertEqual(2, len(adi_dict['RECORDS']))
        self.assertDictEqual(rec_dict, adi_dict['RECORDS'][0])

    def test_70_loadi(self):
        adi_txt = '''<QSO_DATE:8>20231008 <TIME_ON:4>1145 <CALL:6>dl4bdf<eor>
<QSO_DATE:8>20231008 <TIME_ON:4>1146 <CALL:6>DL5HJK <NAME:5>Peter <eor>
<QSO_DATE:8>20231008 <TIME_ON:4>1340 <RST_SENT:2>59<eor>
<QSO_DATE:8>20231008 <TIME_ON:4>1754<eor>
<eor>
<QSO_DATE:8>20231008 <MODE:2>AM <eor>'''

        rec_list = ({},
                    {'QSO_DATE': '20231008', 'TIME_ON': '1340', 'RST_SENT': '59'},
                    {'QSO_DATE': '20231008', 'TIME_ON': '1754'},
                    {},
                    {'QSO_DATE': '20231008', 'MODE': 'AM'})

        for exp, rec in zip(rec_list, adif_file.adi.loadi(adi_txt, 2)):
            self.assertDictEqual(exp, rec)

    def test_80_utf8file(self):
        adi_dict = adif_file.adi.load(get_file_path('testdata/utf8file.txt'), encoding='utf8')

        self.assertIn('HEADER', adi_dict)
        self.assertIn('RECORDS', adi_dict)
        self.assertEqual(3, len(adi_dict['HEADER']))
        self.assertEqual(5, len(adi_dict['RECORDS']))
        self.assertEqual('Jörg', adi_dict['RECORDS'][4]['NAME'])

    def test_81_latin1file(self):
        adi_dict = adif_file.adi.load(get_file_path('testdata/latin1file.txt'), encoding='latin1')

        self.assertIn('HEADER', adi_dict)
        self.assertIn('RECORDS', adi_dict)
        self.assertEqual(3, len(adi_dict['HEADER']))
        self.assertEqual(5, len(adi_dict['RECORDS']))
        self.assertEqual('Jörg', adi_dict['RECORDS'][4]['NAME'])


if __name__ == '__main__':
    unittest.main()
