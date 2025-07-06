# PyADIF-File (c) 2025 by Andreas Schawo is licensed under CC BY-SA 4.0.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/

import unittest

from adif_file.util import *


class Util(unittest.TestCase):
    def test_10_conv_adfidate(self):
        self.assertEqual('2025-04-25', adif_date2iso('20250425'))
        self.assertRaises(ValueError, adif_date2iso, '2025042')

    def test_20_conv_adfitime(self):
        self.assertEqual('11:25', adif_time2iso('1125'))
        self.assertEqual('18:33:45', adif_time2iso('183345'))
        self.assertRaises(ValueError, adif_time2iso, '18334')

    def test_30_conv_isodate(self):
        self.assertEqual('20250425', iso_date2adif('2025-04-25'))
        self.assertRaises(ValueError, iso_date2adif, '2025-042')

    def test_40_conv_isotime(self):
        self.assertEqual('1125', iso_time2adif('11:25'))
        self.assertEqual('183345', iso_time2adif('18:33:45'))
        self.assertRaises(ValueError, iso_time2adif, '20:2542')
        self.assertRaises(ValueError, iso_time2adif, '7:25')

    def test_100_call_format(self):
        self.assertTrue(check_format(REGEX_CALL, 'Df1ASC'))
        self.assertTrue(check_format(REGEX_CALL, 'DF1ASc/P'))
        self.assertTrue(check_format(REGEX_CALL, 'HB9/dF1ASC'))
        self.assertFalse(check_format(REGEX_CALL, 'HB9/DF1ASC/MOBILE'))
        self.assertFalse(check_format(REGEX_CALL, 'DF1 ASC'))
        self.assertTrue(check_format(REGEX_CALL, '2N2XCV'))
        self.assertTrue(check_format(REGEX_CALL, 'N2X'))

    def test_105_check_call(self):
        self.assertTupleEqual((None, 'DF1ASC', None), check_call('DF1ASC'))
        self.assertTupleEqual((None, 'DF1ASC', '/m'), check_call('DF1ASC/m'))
        self.assertTupleEqual(('HB9/', 'DF1ASC', None), check_call('HB9/DF1ASC'))
        self.assertTupleEqual(('HB9/', 'DF1ASC', '/MM'), check_call('HB9/DF1ASC/MM'))
        self.assertIsNone(check_call('HB9/DF1ASC/MOBILE'))
        self.assertIsNone(check_call('DF1 ASC'))

    def test_110_adifdate_format(self):
        self.assertTrue(check_format(REGEX_ADIFDATE, '20251231'))
        self.assertFalse(check_format(REGEX_ADIFDATE, '2025-12-31'))
        self.assertFalse(check_format(REGEX_ADIFDATE, '251231'))
        self.assertFalse(check_format(REGEX_ADIFDATE, '20251331'))
        self.assertFalse(check_format(REGEX_ADIFDATE, '20250132'))

    def test_120_adiftime_format(self):
        self.assertTrue(check_format(REGEX_ADIFTIME, '2359'))
        self.assertTrue(check_format(REGEX_ADIFTIME, '235959'))
        self.assertFalse(check_format(REGEX_ADIFTIME, '617'))
        self.assertFalse(check_format(REGEX_ADIFTIME, '06:17'))
        self.assertFalse(check_format(REGEX_ADIFTIME, '6:17'))
        self.assertFalse(check_format(REGEX_ADIFTIME, '1260'))

    def test_130_isodate_format(self):
        self.assertTrue(check_format(REGEX_ISODATE, '2025-12-31'))
        self.assertFalse(check_format(REGEX_ISODATE, '20251231'))
        self.assertFalse(check_format(REGEX_ISODATE, '25-12-31'))
        self.assertFalse(check_format(REGEX_ISODATE, '2025-13-31'))
        self.assertFalse(check_format(REGEX_ISODATE, '2025-01-32'))

    def test_140_isotime_format(self):
        self.assertTrue(check_format(REGEX_ISOTIME, '23:59'))
        self.assertTrue(check_format(REGEX_ISOTIME, '23:59:59'))
        self.assertFalse(check_format(REGEX_ISOTIME, '6:17'))
        self.assertFalse(check_format(REGEX_ISOTIME, '0617'))
        self.assertFalse(check_format(REGEX_ISOTIME, '617'))
        self.assertFalse(check_format(REGEX_ISOTIME, '12:60'))

    def test_150_locator_format(self):
        self.assertTrue(check_format(REGEX_LOCATOR, 'aa11'))
        self.assertTrue(check_format(REGEX_LOCATOR, 'aa11gg'))
        self.assertTrue(check_format(REGEX_LOCATOR, 'aa11gg99'))
        self.assertTrue(check_format(REGEX_LOCATOR, 'aa00ff'))
        self.assertTrue(check_format(REGEX_LOCATOR, 'RR99xx'))
        self.assertFalse(check_format(REGEX_LOCATOR, 'aa99zz'))
        self.assertFalse(check_format(REGEX_LOCATOR, 'zz99aa'))
        self.assertFalse(check_format(REGEX_LOCATOR, 'aa54e'))
        self.assertFalse(check_format(REGEX_LOCATOR, 'aa5ee'))

    def test_160_rst_format(self):
        self.assertTrue(check_format(REGEX_RST, '59'))
        self.assertTrue(check_format(REGEX_RST, '599'))
        self.assertTrue(check_format(REGEX_RST, '597m'))
        self.assertTrue(check_format(REGEX_RST, '111A'))
        self.assertFalse(check_format(REGEX_RST, '11A'))
        self.assertFalse(check_format(REGEX_RST, '01'))
        self.assertFalse(check_format(REGEX_RST, '10'))

        # Digi modes
        self.assertTrue(check_format(REGEX_RST, '12'))
        self.assertTrue(check_format(REGEX_RST, '+12'))
        self.assertTrue(check_format(REGEX_RST, '+6'))
        self.assertTrue(check_format(REGEX_RST, '-5'))
        self.assertTrue(check_format(REGEX_RST, '-35'))
        self.assertFalse(check_format(REGEX_RST, '+100'))
        self.assertFalse(check_format(REGEX_RST, '-223'))

    def test_200_replace_nonascii(self):
        txt_non_ascii = 'Es saß ´ne hübsche YL am Funkegrät und funkte, nach Östereich auf 70cm sie blödelte und unkte'
        txt_ascii_default = 'Es sa_ _ne h_bsche YL am Funkegr_t und funkte, nach _stereich auf 70cm sie bl_delte und unkte'
        txt_ascii_defsharp = 'Es sa# #ne h#bsche YL am Funkegr#t und funkte, nach #stereich auf 70cm sie bl#delte und unkte'
        txt_ascii_de = 'Es sass \'ne huebsche YL am Funkegraet und funkte, nach Oestereich auf 70cm sie bloedelte und unkte'
        ascii_map = {'ß':'ss', '´':'\'', 'ä': 'ae', 'ö': 'oe', 'Ö': 'Oe', 'ü': 'ue'}
        self.assertEqual(txt_ascii_default, replace_non_ascii(txt_non_ascii))
        self.assertEqual(txt_ascii_defsharp, replace_non_ascii(txt_non_ascii, default='#'))
        self.assertEqual(txt_ascii_de, replace_non_ascii(txt_non_ascii, ascii_map))
