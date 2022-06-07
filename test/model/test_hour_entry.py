import unittest
from podap.model import HourEntry


class HourEntryTest(unittest.TestCase):
    def test_str_formatting(self):
        entry = HourEntry(start_hour=7, title='test')
        self.assertEqual(str(entry), 'test\n07:00')

    def test_parser(self):
        with self.assertRaises(ValueError):
            HourEntry.parse('foo10:00')

        with self.assertRaises(ValueError):
            HourEntry.parse('foo\n1000')

        with self.assertRaises(ValueError):
            HourEntry.parse('foo\nbar:00')

        entry = HourEntry.parse('foo\n7:00')
        self.assertEqual(entry.start_hour, 7)
        self.assertEqual(entry.title, 'foo')


if __name__ == '__main__':
    unittest.main()
