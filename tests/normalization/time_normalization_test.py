import unittest
from datetime import datetime

from rscraping.data.normalization import normalize_lap_time


class TestTimeNormalization(unittest.TestCase):
    def setUp(self) -> None:
        self.TIMES = [
            ":18,62",
            ":45",
            "2102:48",
            "25:2257",
            "028:24",
            "00:009",
            "21.13.66",
        ]

    def test_lap_time_normalization(self):
        results = [
            "00:18.62",
            "00:45.00",
            "21:02.48",
            "25:22.57",
            "28:24.00",
            "00:00.00",
            "21:13.66",
        ]

        for idx, lap_time in enumerate(self.TIMES):
            self.assertEqual(normalize_lap_time(lap_time), datetime.strptime(results[idx], "%M:%S.%f").time())
