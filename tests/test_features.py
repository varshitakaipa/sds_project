import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import features

class FeatureTests(unittest.TestCase):
    def row(self, **changes):
        r = dict(MEAN_MOTION=15.5, ECCENTRICITY=0, INCLINATION=53, EPOCH='2026-11-14T00:00:00', NORAD_CAT_ID=123456, OBJECT_NAME='TEST')
        r.update(changes)
        return r
    def test_circular_orbit_and_large_catalog_id(self):
        f = features(self.row())
        self.assertAlmostEqual(f['period_minutes'], 1440/15.5)
        self.assertTrue(400 < f['mean_altitude_proxy_km'] < 450)
        self.assertEqual(f['perigee_proxy_km'], f['apogee_proxy_km'])
        self.assertEqual(f['norad_id'], 123456)
    def test_invalid_elements(self):
        for change in ({'MEAN_MOTION': 0}, {'ECCENTRICITY': 1}, {'INCLINATION': 181}, {'MEAN_MOTION': float('nan')}):
            with self.assertRaises(ValueError): features(self.row(**change))

if __name__ == '__main__': unittest.main()
