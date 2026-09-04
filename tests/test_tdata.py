import tempfile
import unittest
from pathlib import Path

from tdl_companionwulf.tdata import (
    TdataLease,
    candidate_from_path,
    discover_known_tdata,
    stable_hex_hash,
)
from tdl_companionwulf.tdl import TdlOptions, build_login_command


class TdataCandidateTests(unittest.TestCase):
    def test_candidate_requires_tdata_directory(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self.assertIsNone(candidate_from_path(root, "known"))
    def test_candidate_reports_key_data(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "Telegram Desktop" / "tdata"
            path.mkdir(parents=True)
            (path / "key_data").write_bytes(b"x")
            candidate = candidate_from_path(path, "known")
            self.assertIsNotNone(candidate)
            self.assertTrue(candidate.has_key_data)
            self.assertEqual(candidate.path, path.resolve())

    def test_discovery_deduplicates_known_paths(self):
        with tempfile.TemporaryDirectory() as name:
            home = Path(name)
            path = home / "Telegram Desktop" / "tdata"
            path.mkdir(parents=True)
            found = discover_known_tdata(home=home, extra_paths=[path, path])
            self.assertEqual([item.path for item in found], [path.resolve()])


class TdataLeaseTests(unittest.TestCase):
    def test_stable_hash_is_repeatable(self):
        self.assertEqual(stable_hex_hash("abc"), stable_hex_hash("abc"))
        self.assertEqual(len(stable_hex_hash("abc")), 64)

    def test_second_lease_is_blocked_until_release(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            tdata = root / "tdata"
            tdata.mkdir()
            first = TdataLease(tdata, root / "locks", namespace="one")
            second = TdataLease(tdata, root / "locks", namespace="two")
            self.assertTrue(first.acquire())
            self.assertFalse(second.acquire())
            first.release()
            self.assertTrue(second.acquire())
            second.release()


class TdlLoginCommandTests(unittest.TestCase):
    def test_builds_desktop_login_command_for_namespace(self):
        command = build_login_command(
            "tdl",
            TdlOptions(namespace="family"),
            Path("/tmp/Telegram Desktop/tdata"),
        )
        self.assertEqual(
            command,
            ["tdl", "login", "-n", "family", "-d", "/tmp/Telegram Desktop/tdata"],
        )


class AuthCliTests(unittest.TestCase):
    def test_parser_exposes_auth_status_candidates_and_login(self):
        from tdl_companionwulf import cli

        status = cli.build_parser().parse_args(["auth", "status", "--namespace", "family"])
        self.assertEqual((status.command, status.auth_command), ("auth", "status"))
        candidates = cli.build_parser().parse_args(["auth", "candidates"])
        self.assertEqual(candidates.auth_command, "candidates")
        login = cli.build_parser().parse_args(["auth", "login", "--tdata", "/tmp/tdata"])
        self.assertEqual(login.tdata, Path("/tmp/tdata"))


class TdataAuthFlowTests(unittest.TestCase):
    @unittest.skipIf(__import__("os").name == "nt", "POSIX fake executable launcher")
    def test_login_flow_saves_namespace_association(self):
        import os
        import stat
        from unittest import mock
        from tdl_companionwulf import cli

        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            tdata = root / "Telegram Desktop" / "tdata"
            tdata.mkdir(parents=True)
            (tdata / "key_data").write_bytes(b"x")
            log = root / "calls.log"
            fake = root / "tdl"
            fake.write_text(
                f'''#!/usr/bin/env python3
import json, pathlib, sys
pathlib.Path({str(log)!r}).open("a", encoding="utf-8").write(json.dumps(sys.argv[1:]) + "\\n")
if "chat" in sys.argv and "ls" in sys.argv:
    print("[]")
sys.exit(0)
''',
                encoding="utf-8",
            )
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            with mock.patch.dict(os.environ, {"XDG_STATE_HOME": str(root / "state")}, clear=False):
                code = cli.login_tdata(str(fake), TdlOptions(namespace="family"), tdata)
                self.assertEqual(code, 0)
                self.assertEqual(cli.get_namespace_tdata("family"), tdata.resolve())
                self.assertEqual(len(log.read_text(encoding="utf-8").splitlines()), 2)


class LegacyKnownPathTests(unittest.TestCase):
    def test_discovers_igram_desktop_tdata(self):
        with tempfile.TemporaryDirectory() as name:
            home = Path(name)
            tdata = home / "iGram Desktop" / "tdata"
            tdata.mkdir(parents=True)
            found = discover_known_tdata(home=home, env={})
            self.assertIn(tdata.resolve(), [item.path for item in found])
