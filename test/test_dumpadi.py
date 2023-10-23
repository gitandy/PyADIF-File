import unittest

from adif_file import *


class DumpADI(unittest.TestCase):
    def test_10_pack_header_tag(self):
        self.assertEqual('<PROGRAMID:8>Testprog', pack('PROGRAMID', 'Testprog'))
        self.assertEqual('<USERDEF1:4:N>Test', pack('USERDEF1', 'Test', 'N'))
        self.assertEqual('<USERDEF1:19:E>SweaterSize,{S,M,L}',
                         pack('USERDEF1', 'SweaterSize,{S,M,L}', 'E'))

        self.assertRaises(UnknownDataTypeException, pack, 'USERDEF1', 'SweaterSize,{S,M,L}', 'X')
        self.assertRaises(UnknownDataTypeException, pack, 'USERDEF1', 'SweaterSize,{S,M,L}', 'NN')

    def test_15_pack_record_tag(self):
        self.assertEqual('<NAME:5>Joerg', pack('NAME', 'Joerg'))
        self.assertEqual('<NAME:5>Joerg', pack('name', 'Joerg'))
        self.assertEqual('<NAME:5>Joerg', pack('Name', 'Joerg'))
        self.assertEqual('', pack('name_intl', 'Joerg'))

        self.assertEqual('<MY_NAME:5>Peter', pack('MY_Name', 'Peter'))

        self.assertRaises(StringNotASCIIException, pack, 'NAME', 'Jörg')
        self.assertRaises(StringNotASCIIException, pack, 'NAME', 'Schloß')
        self.assertRaises(IllegalParameterException, pack, 'MY_ NAME', 'Peter')
        self.assertRaises(IllegalParameterException, pack, 'MY~NAME', 'Peter')

        # noinspection PyTypeChecker
        self.assertEqual('<DIST:2>99', pack('DIST', 99))
        # noinspection PyTypeChecker
        self.assertEqual('<FREQ:5>0.138', pack('freq', 0.138))

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

        self.assertEqual(exp_hdr, dict2adi(adi_dict))

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
        self.assertEqual(exp_hdr_udef, dict2adi(adi_dict))

    def test_25_dump_records(self):
        adi_dict = {
            'RECORDS': [{'TEST1': 'test',
                         'TEST2': 'test2'},
                        {'TEST1': 'test3',
                         'TEST2': 'test4'}]}

        adi_exp = '''<TEST1:4>test <TEST2:5>test2 
<EOR>

<TEST1:5>test3 <TEST2:5>test4 
<EOR>'''

        self.assertEqual(adi_exp, dict2adi(adi_dict))




if __name__ == '__main__':
    unittest.main()
