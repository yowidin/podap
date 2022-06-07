import unittest
from podap.model import HourEntry, DayEntry, DayOfWeek


class DayEntryTestCase(unittest.TestCase):
    def test_str_formatting(self):
        entry = DayEntry(day_of_week=DayOfWeek.Monday, entries=[HourEntry(1, 'foo'), HourEntry(2, 'bar')])
        self.assertEqual(str(entry), 'foo\n01:00\n\nbar\n02:00')

        test = str(entry).split('\n\n')
        print(test)

    def test_parser(self):
        with self.assertRaises(ValueError):
            # Make sure that HourEntry exceptions are propagated
            DayEntry.parse(DayOfWeek.Monday, 'foon10:00')

        entry = DayEntry.parse(DayOfWeek.Tuesday, 'foo\n7:00\n\nbar\n8:00')
        self.assertEqual(entry.day_of_week, DayOfWeek.Tuesday)
        self.assertEqual(len(entry.entries), 2)
        self.assertEqual(entry.entries[0].start_hour, 7)
        self.assertEqual(entry.entries[0].title, 'foo')
        self.assertEqual(entry.entries[1].start_hour, 8)
        self.assertEqual(entry.entries[1].title, 'bar')


if __name__ == '__main__':
    unittest.main()
