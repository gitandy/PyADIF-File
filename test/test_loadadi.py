import unittest

from adif_file import *


class LoadADI(unittest.TestCase):
    def test_10_unpack_header(self):
        adi_hdr1 = '''ADIF Export by Testprog
<ADIF_VER:5>3.1.4 <PROGRAMID:8>Testprog <PROGRAMVERSION:4>v0.2'''
        adi_hdr2 = '''ADIF Export by Testprog
    <ADIF_VER:5>3.1.4
    <PROGRAMID:8>Testprog 
    <PROGRAMVERSION:4>v0.2'''
        exp_dict = {'ADIF_VER': '3.1.4', 'PROGRAMID': 'Testprog', 'PROGRAMVERSION': 'v0.2'}

        self.assertDictEqual(exp_dict, unpack(adi_hdr1))
        self.assertDictEqual(exp_dict, unpack(adi_hdr2))

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

        self.assertDictEqual(exp_dict1, unpack(adi_hdr1))
        self.assertDictEqual(exp_dict2, unpack(adi_hdr2))

    def test_20_goodfile(self):
        with open('testdata/goodfile.txt', encoding='ascii') as tf:
            adi_txt = tf.read()

        adi_dict = adi2dict(adi_txt)

        self.assertIn('HEADER', adi_dict)
        self.assertIn('RECORDS', adi_dict)
        self.assertEqual(3, len(adi_dict['HEADER']))
        self.assertEqual(5, len(adi_dict['RECORDS']))

    def test_25_toomuchheaders(self):
        with open('testdata/toomuchheadersfile.txt', encoding='ascii') as tf:
            adi_txt = tf.read()

        self.assertRaises(TooMuchHeadersException, adi2dict, adi_txt)


if __name__ == '__main__':
    unittest.main()
