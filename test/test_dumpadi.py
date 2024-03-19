import os
import unittest

import adif_file.adi


def get_file_path(file):
    return os.path.join(os.path.dirname(__file__), file)


class DumpADI(unittest.TestCase):
    def test_10_pack_header_tag(self):
        self.assertEqual('<PROGRAMID:8>Testprog', adif_file.adi.pack('PROGRAMID', 'Testprog'))
        self.assertEqual('<USERDEF1:4:N>Test', adif_file.adi.pack('USERDEF1', 'Test', 'N'))
        self.assertEqual('<USERDEF1:19:E>SweaterSize,{S,M,L}',
                         adif_file.adi.pack('USERDEF1', 'SweaterSize,{S,M,L}', 'E'))

        self.assertRaises(adif_file.adi.IllegalDataTypeException, adif_file.adi.pack, 'USERDEF1', 'SweaterSize,{S,M,L}', 'X')
        self.assertRaises(adif_file.adi.IllegalDataTypeException, adif_file.adi.pack, 'USERDEF1', 'SweaterSize,{S,M,L}', 'NN')

    def test_15_pack_record_tag(self):
        self.assertEqual('<NAME:5>Joerg', adif_file.adi.pack('NAME', 'Joerg'))
        self.assertEqual('<NAME:5>Joerg', adif_file.adi.pack('name', 'Joerg'))
        self.assertEqual('<NAME:5>Joerg', adif_file.adi.pack('Name', 'Joerg'))
        self.assertEqual('', adif_file.adi.pack('name_intl', 'Joerg'))
        self.assertEqual('<APP_TESTAPP_CHANNEL:2:N>24', adif_file.adi.pack('APP_TESTAPP_CHANNEL', 24, dtype='N'))

        self.assertEqual('<MY_NAME:5>Peter', adif_file.adi.pack('MY_Name', 'Peter'))

        self.assertRaises(adif_file.adi.StringNotASCIIException, adif_file.adi.pack, 'NAME', 'Jörg')
        self.assertRaises(adif_file.adi.StringNotASCIIException, adif_file.adi.pack, 'NAME', 'Schloß')
        self.assertRaises(adif_file.adi.IllegalParameterException, adif_file.adi.pack, 'MY_ NAME', 'Peter')
        self.assertRaises(adif_file.adi.IllegalParameterException, adif_file.adi.pack, 'MY~NAME', 'Peter')

        # noinspection PyTypeChecker
        self.assertEqual('<DIST:2>99', adif_file.adi.pack('DIST', 99))
        # noinspection PyTypeChecker
        self.assertEqual('<FREQ:5>0.138', adif_file.adi.pack('freq', 0.138))

    def test_20_dump_header(self):
        adi_dict = {
            'HEADER': {'PROGRAMID': 'TProg',
                       'ADIF_VER': '3',
                       'PROGRAMVERSION': '1',
                       'CREATED_TIMESTAMP': '1234'},
        }

        exp_hdr = '''ADIF export by PyADIF-File 
<PROGRAMID:5>TProg
<ADIF_VER:1>3
<PROGRAMVERSION:1>1
<CREATED_TIMESTAMP:4>1234
<EOH>'''

        self.assertEqual(exp_hdr, adif_file.adi.dumps(adi_dict))

        # Test same with udef
        adi_udef = [{'dtype': 'E',
                     'userdef': 'Test,{A,B,C}'},
                    {'dtype': 'N',
                     'userdef': 'Test2,{5:20}'}]

        exp_hdr_udef = '''ADIF export by PyADIF-File 
<PROGRAMID:5>TProg
<ADIF_VER:1>3
<PROGRAMVERSION:1>1
<CREATED_TIMESTAMP:4>1234
<USERDEF1:12:E>Test,{A,B,C}
<USERDEF2:12:N>Test2,{5:20}
<EOH>'''

        adi_dict['HEADER']['USERDEFS'] = adi_udef
        self.assertEqual(exp_hdr_udef, adif_file.adi.dumps(adi_dict))

    def test_25_dump_records(self):
        adi_dict = {
            'RECORDS': [{'TEST1': 'test',
                         'TEST2': 'test2'},
                        {'TEST1': 'test3',
                         'TEST2': 'test4\r\ntest5'}]}

        adi_exp = '''<TEST1:4>test <TEST2:5>test2 
<EOR>

<TEST1:5>test3 <TEST2:12>test4\r\ntest5 
<EOR>'''

        self.assertEqual(adi_exp, adif_file.adi.dumps(adi_dict))

    def test_30_dump_a_file(self):
        adi_dict = {
            'HEADER': {'PROGRAMID': 'TProg',
                       'ADIF_VER': '3',
                       'PROGRAMVERSION': '1',
                       'CREATED_TIMESTAMP': '1234'},
            'RECORDS': [{'TEST1': 'test',
                         'TEST2': 'test2'},
                        {'TEST1': 'test3',
                         'TEST2': 'test4'}]
        }

        adi_exp = '''ADIF export by PyADIF-File 
<PROGRAMID:5>TProg
<ADIF_VER:1>3
<PROGRAMVERSION:1>1
<CREATED_TIMESTAMP:4>1234
<EOH>

<TEST1:4>test <TEST2:5>test2 
<EOR>

<TEST1:5>test3 <TEST2:5>test4 
<EOR>'''

        temp_file = get_file_path('testdata/~test.adi')

        adif_file.adi.dump(temp_file, adi_dict)

        self.assertTrue(os.path.isfile(temp_file))

        with open(temp_file) as af:
            self.assertEqual(adi_exp, af.read())

        os.remove(temp_file)

    def test_31_dump_a_file_ln_sp(self):
            adi_dict = {
                'HEADER': {'PROGRAMID': 'TProg',
                           'ADIF_VER': '3',
                           'PROGRAMVERSION': '1',
                           'CREATED_TIMESTAMP': '1234'},
                'RECORDS': [{'TEST1': 'test',
                             'TEST2': 'test2'},
                            {'TEST1': 'test3',
                             'TEST2': 'test4'}]
            }

            adi_exp = '''ADIF export by PyADIF-File 
<PROGRAMID:5>TProg  <ADIF_VER:1>3  <PROGRAMVERSION:1>1  <CREATED_TIMESTAMP:4>1234  <EOH>
<TEST1:4>test  <TEST2:5>test2  <EOR>
<TEST1:5>test3  <TEST2:5>test4  <EOR>'''

            temp_file = get_file_path('testdata/~test.adi')

            adif_file.adi.dump(temp_file, adi_dict, linebreaks=False, spaces=2)

            self.assertTrue(os.path.isfile(temp_file))

            with open(temp_file) as af:
                self.assertEqual(adi_exp, af.read())

            os.remove(temp_file)

    def test_40_dump_no_change(self):
        adi_dict = {
            'HEADER': {'PROGRAMID': 'TProg',
                       'PROGRAMVERSION': '1',
                       'CREATED_TIMESTAMP': '1234'},
            'RECORDS': [{'TEST1': 'test',
                         'TEST2': 'test2'},
                        {'TEST1': 'test3',
                         'TEST2': 'test4'}]
        }
        adi_dict_sav = adi_dict.copy()

        adi_exp = '''ADIF export by PyADIF-File 
<PROGRAMID:5>TProg
<PROGRAMVERSION:1>1
<CREATED_TIMESTAMP:4>1234
<ADIF_VER:5>3.1.4
<EOH>

<TEST1:4>test <TEST2:5>test2 
<EOR>

<TEST1:5>test3 <TEST2:5>test4 
<EOR>'''

        temp_file = get_file_path('testdata/~test.adi')

        adif_file.adi.dump(temp_file, adi_dict)
        self.assertDictEqual(adi_dict_sav, adi_dict)

        self.assertTrue(os.path.isfile(temp_file))

        with open(temp_file) as af:
            self.assertEqual(adi_exp, af.read())

        os.remove(temp_file)


if __name__ == '__main__':
    unittest.main()
