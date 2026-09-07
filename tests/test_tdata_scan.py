import tempfile
import unittest
from pathlib import Path

from tdl_companionwulf.tdata import find_system_tdata, scan_volume_roots


class TdataScanTests(unittest.TestCase):
    def test_recursive_scan_finds_tdata_and_prioritizes_key_data(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            first = root / "a" / "tdata"
            second = root / "b" / "tdata"
            first.mkdir(parents=True)
            second.mkdir(parents=True)
            (second / "key_data").write_bytes(b"x")
            found = find_system_tdata([root])
            self.assertEqual([item.path for item in found], [second.resolve(), first.resolve()])

    def test_excluded_candidate_is_not_returned(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            candidate = root / "Telegram" / "tdata"
            candidate.mkdir(parents=True)
            (candidate / "key_data").write_bytes(b"x")
            self.assertEqual(find_system_tdata([root], exclude=[candidate]), [])

    def test_max_directories_bounds_scan(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            candidate = root / "a" / "b" / "c" / "tdata"
            candidate.mkdir(parents=True)
            self.assertEqual(find_system_tdata([root], max_directories=1), [])

    def test_scan_volume_roots_returns_existing_roots(self):
        roots = scan_volume_roots()
        self.assertTrue(roots)
        self.assertTrue(all(root.exists() for root in roots))


if __name__ == "__main__":
    unittest.main()
