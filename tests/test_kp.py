import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyze_kp import validate, events

class KpTests(unittest.TestCase):
    def data(self):
        return dict(datetime=['2026-10-01T00:00:00Z','2026-10-01T03:00:00Z','2026-10-01T09:00:00Z'],Kp=[5,6,5],status=['def','pre','pre'])
    def test_gap_splits_events_and_end_is_exclusive(self):
        e=events(validate(self.data()))
        self.assertEqual([x['bins'] for x in e],[2,1])
        self.assertEqual(e[0]['end'].hour,6)
    def test_bad_values_and_lengths(self):
        for value in (float('nan'),-1,10,True):
            d=self.data(); d['Kp'][0]=value
            with self.assertRaises(ValueError): validate(d)
        d=self.data(); d['status'].pop()
        with self.assertRaises(ValueError): validate(d)
    def test_duplicate_and_off_grid(self):
        for stamp in ('2026-10-01T03:00:00Z','2026-10-01T01:00:00Z'):
            d=self.data(); d['datetime'][0]=stamp
            with self.assertRaises(ValueError): validate(d)

if __name__=='__main__': unittest.main()
