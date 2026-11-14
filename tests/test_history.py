import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyze_history import utc, bin_start, rate

class HistoryTests(unittest.TestCase):
    def test_utc_bins(self):
        t=utc('2026-10-01T05:59:59')
        self.assertEqual(bin_start(t,3).hour,3)
        self.assertEqual(t.utcoffset().total_seconds(),0)
    def test_rate_and_gap_exclusion(self):
        a=dict(epoch='2026-10-01T00:00:00Z',mean_altitude_proxy_km=500)
        b=dict(epoch='2026-10-02T00:00:00Z',mean_altitude_proxy_km=498)
        self.assertEqual(rate(a,b),-2)
        self.assertIsNone(rate(a,a))
        b['epoch']='2026-10-04T00:00:00Z'
        self.assertIsNone(rate(a,b))

if __name__=='__main__': unittest.main()
