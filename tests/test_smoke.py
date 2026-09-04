import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tdl_companionwulf import cli


class CompanionSmokeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.local = Path(self.temp.name)
        self.env = mock.patch.dict(
            os.environ,
            {"LOCALAPPDATA": str(self.local), "XDG_STATE_HOME": str(self.local)},
            clear=False,
        )
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_add_and_queue(self):
        job_id = cli.add_url("https://t.me/example_test_entry", 75)
        self.assertGreater(job_id, 0)
        rows = cli.queue_rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["priority"], 75)
        self.assertEqual(rows[0]["status"], "waiting")

    def test_duplicate_url_reuses_job(self):
        first = cli.add_url("https://t.me/example_test_entry")
        second = cli.add_url("https://t.me/example_test_entry")
        self.assertEqual(first, second)
        self.assertEqual(len(cli.queue_rows()), 1)

    def test_database_is_created_in_state_directory(self):
        path = cli.db_path()
        self.assertTrue(str(path).startswith(str(self.local)))
        with cli.connect():
            pass
        self.assertTrue(path.is_file())

    def test_settings_round_trip(self):
        cli.set_setting("namespace", "family")
        self.assertEqual(cli.get_setting("namespace"), "family")
        self.assertEqual(dict(cli.list_settings())["namespace"], "family")
        self.assertTrue(cli.unset_setting("namespace"))
        self.assertIsNone(cli.get_setting("namespace"))


# Connection lifecycle regression test.
class ConnectionLifecycleTests(unittest.TestCase):
    def test_connection_context_closes_database(self):
        import sqlite3

        with tempfile.TemporaryDirectory() as temp:
            with mock.patch.dict(
                os.environ,
                {"LOCALAPPDATA": temp, "XDG_STATE_HOME": temp},
                clear=False,
            ):
                conn = cli.connect()
                with conn:
                    conn.execute("SELECT 1")
                with self.assertRaises(sqlite3.ProgrammingError):
                    conn.execute("SELECT 1")


if __name__ == "__main__":
    unittest.main()
