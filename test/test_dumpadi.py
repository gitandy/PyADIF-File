import os
import unittest

import adif_file.adi


def get_file_path(file):
    return os.path.join(os.path.dirname(__file__), file)


class DumpADI(unittest.TestCase):
    def test_10_pack_header_tag(self):
        self.assertEqual('<PROGRAMID:8>Testprog', adif_file.adi.pack('PROGRAMID', 'Testprog', validate=False))
        self.assertEqual('<USERDEF1:4:N>Test', adif_file.adi.pack('USERDEF1', 'Test', 'N', validate=False))
        self.assertEqual('<USERDEF1:19:E>SweaterSize,{S,M,L}',
                         adif_file.adi.pack('USERDEF1', 'SweaterSize,{S,M,L}', 'E', validate=False))

        self.assertRaises(adif_file.adi.IllegalDataTypeException, adif_file.adi.pack, 'USERDEF1', 'SweaterSize,{S,M,L}', 'X', False)
        self.assertRaises(adif_file.adi.IllegalDataTypeException, adif_file.adi.pack, 'USERDEF1', 'SweaterSize,{S,M,L}', 'NN', False)

    def test_12_pack_header_validate(self):
        self.assertEqual('<PROGRAMID:8>Testprog', adif_file.adi.pack('PROGRAMID', 'Testprog', validate=True, header=True))
        self.assertEqual('<USERDEF1:4:N>Test', adif_file.adi.pack('USERDEF1', 'Test', 'N', validate=True, header=True))
        self.assertEqual('<USERDEF1:19:E>SweaterSize,{S,M,L}',
                         adif_file.adi.pack('USERDEF1', 'SweaterSize,{S,M,L}', 'E', validate=True, header=True))

        self.assertRaises(adif_file.adi.IllegalFieldNameException,
                          adif_file.adi.pack, 'XXXXX', 'Undef', None, True, True)
        self.assertRaises(adif_file.adi.IllegalFieldNameException,
                          adif_file.adi.pack, 'USERDEF2', 'Name', 'S', True, True)

    def test_15_pack_record_tag(self):
        self.assertEqual('<NAME:5>Joerg', adif_file.adi.pack('NAME', 'Joerg'))
        self.assertEqual('<NAME:5>Joerg', adif_file.adi.pack('name', 'Joerg'))
        self.assertEqual('<NAME:5>Joerg', adif_file.adi.pack('Name', 'Joerg'))
        self.assertEqual('', adif_file.adi.pack('name_intl', 'Joerg', validate=False))
        self.assertEqual('<APP_TESTAPP_CHANNEL:2:N>24', adif_file.adi.pack('APP_TESTAPP_CHANNEL', 24, dtype='N'))

        self.assertEqual('<MY_NAME:5>Peter', adif_file.adi.pack('MY_Name', 'Peter'))

        self.assertRaises(adif_file.adi.StringNotASCIIException, adif_file.adi.pack, 'NAME', 'Jörg')
        self.assertRaises(adif_file.adi.StringNotASCIIException, adif_file.adi.pack, 'NAME', 'Schloß')
        self.assertRaises(adif_file.adi.IllegalParameterException, adif_file.adi.pack, 'MY_ NAME', 'Peter')
        self.assertRaises(adif_file.adi.IllegalParameterException, adif_file.adi.pack, 'MY~NAME', 'Peter')

        # noinspection PyTypevalidateer
        self.assertEqual('<DISTANCE:2>99', adif_file.adi.pack('DISTANCE', 99))
        # noinspection PyTypevalidateer
        self.assertEqual('<FREQ:5>0.138', adif_file.adi.pack('freq', 0.138))

    def test_17_pack_record_validate(self):
        self.assertEqual('<NAME:5>Joerg', adif_file.adi.pack('NAME', 'Joerg', validate=True))
        self.assertEqual('<NAME:5>Joerg', adif_file.adi.pack('name', 'Joerg', validate=True))
        self.assertEqual('<NAME:5>Joerg', adif_file.adi.pack('Name', 'Joerg', validate=True))
        self.assertEqual('<APP_TESTAPP_CHANNEL:2:N>24',
                         adif_file.adi.pack('APP_TESTAPP_CHANNEL', 24, dtype='N', validate=True))

        self.assertEqual('<MY_NAME:5>Peter', adif_file.adi.pack('MY_Name', 'Peter', validate=True))

        self.assertRaises(adif_file.adi.IllegalFieldNameException, adif_file.adi.pack, 'XXXXX', 'Undef', None, True)

        self.assertEqual('<XXXXX:7>Userdef',
                         adif_file.adi.pack('XXxXX', 'Userdef', validate=True, userdefs=['XXXXX']))

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

    def test_22_dump_header_defaults(self):
        adif_doc = adif_file.adi.dumps({'HEADER': {}})

        self.assertIn('<ADIF_VER:5>3.1.4', adif_doc)
        self.assertIn('<PROGRAMID:11>PyADIF-File', adif_doc)
        self.assertIn('<PROGRAMVERSION:', adif_doc)
        self.assertIn('<CREATED_TIMESTAMP:', adif_doc)

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

        self.assertEqual(adi_exp, adif_file.adi.dumps(adi_dict, validate=False))

    def test_30_dump_a_file(self):
        adi_dict = {
            'HEADER': {'PROGRAMID': 'TProg',
                       'ADIF_VER': '3',
                       'PROGRAMVERSION': '1',
                       'CREATED_TIMESTAMP': '1234',
                       'USERDEFS': [{'userdef': 'Test', 'dtype': 'N'}]},
            'RECORDS': [{'Name': 'test',
                         'qth': 'test2'},
                        {'name': 'test3',
                         'QTH': 'test4',
                         'test': 'userdef'}]
        }

        adi_exp = '''ADIF export by PyADIF-File 
<PROGRAMID:5>TProg
<ADIF_VER:1>3
<PROGRAMVERSION:1>1
<CREATED_TIMESTAMP:4>1234
<USERDEF1:4:N>Test
<EOH>

<NAME:4>test <QTH:5>test2 
<EOR>

<NAME:5>test3 <QTH:5>test4 <TEST:7>userdef 
<EOR>'''

        temp_file = get_file_path('testdata/~test.adi')

        adif_file.adi.dump(temp_file, adi_dict, validate=True)

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

            adif_file.adi.dump(temp_file, adi_dict, linebreaks=False, spaces=2, validate=False)

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

        adif_file.adi.dump(temp_file, adi_dict, validate=False)
        self.assertDictEqual(adi_dict_sav, adi_dict)

        self.assertTrue(os.path.isfile(temp_file))

        with open(temp_file) as af:
            self.assertEqual(adi_exp, af.read())

        os.remove(temp_file)


if __name__ == '__main__':
    unittest.main()
