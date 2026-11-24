import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from baseline import daily_rows, calibrate, fit, score, screen


class BaselineTests(unittest.TestCase):
    def test_constant_reference_and_signed_outlier(self):
        m=fit([0.]*12)
        self.assertEqual(m['scale'],.02)
        self.assertEqual(score(0,m),0)
        self.assertLess(score(-1,m),-3.5)

    def test_gap_is_not_bridged(self):
        records=[dict(epoch='2026-10-'+d+'T12:00:00+00:00',norad_id='1',mean_altitude_proxy_km=str(h),kp='1') for d,h in [('01',500),('02',499),('04',496)]]
        r=daily_rows(records)
        self.assertEqual(r[1]['rate_km_day'],-1)
        self.assertIsNone(r[2]['rate_km_day'])

    def test_shared_shift_removed_and_local_shift_retained(self):
        records=[]
        for ident in range(7):
            for day in range(1,4):
                records.append(dict(epoch=f'2026-10-0{day}T12:00:00+00:00',norad_id=str(ident),mean_altitude_proxy_km=str(500+day+(2 if ident==0 and day==3 else 0))))
        r=daily_rows(records)
        normal=next(x for x in r if x['norad_id']==1 and x['day']=='2026-10-03')
        changed=next(x for x in r if x['norad_id']==0 and x['day']=='2026-10-03')
        self.assertEqual(normal['peer_residual_km_day'],0)
        self.assertEqual(changed['peer_residual_km_day'],2)

    def test_future_rows_cannot_change_calibration(self):
        train=[dict(norad_id=1,day=f'2026-10-{d:02}',rate_km_day=0.,peer_residual_km_day=0.) for d in range(1,13)]
        future=dict(norad_id=1,day='2026-10-23',rate_km_day=-1.,peer_residual_km_day=-1.)
        m=calibrate(train,'2026-10-22',.02)
        self.assertEqual(m,calibrate(train+[future],'2026-10-22',.02))
        self.assertTrue(screen([future],m,'2026-10-22')[0]['candidate'])
        future['rate_km_day']=0.
        self.assertFalse(screen([future],m,'2026-10-22')[0]['candidate'])

    def test_insufficient_history_and_nonfinite_rejected(self):
        for values in ([0.]*9,[float('nan')]*10):
            with self.assertRaises(ValueError): fit(values)


if __name__=='__main__': unittest.main()
