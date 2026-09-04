import os
import unittest

from tdl_companionwulf.wizard import (
    build_export_jobs,
    parse_chats_json,
    parse_selection,
    safe_component,
)


SAMPLE = r'''[
  {"id": 10, "type": "channel", "visible_name": "News", "username": "news"},
  {"id": 20, "type": "group", "visible_name": "Forum", "topics": [
    {"id": 101, "title": "Music"},
    {"id": 102, "title": "Video"}
  ]}
]'''


class ChatParsingTests(unittest.TestCase):
    def test_parses_tdl_chat_json_and_topics(self):
        chats = parse_chats_json(SAMPLE)
        self.assertEqual([chat.id for chat in chats], [10, 20])
        self.assertEqual(chats[0].name, "News")
        self.assertEqual(chats[1].topics[0].title, "Music")

    def test_uses_username_or_placeholder_when_name_is_missing(self):
        chats = parse_chats_json('[{"id": 1, "type": "private", "username": "andy"}, {"id": 2, "type": "private"}]')
        self.assertEqual(chats[0].name, "andy")
        self.assertEqual(chats[1].name, "(unnamed chat)")


class SelectionTests(unittest.TestCase):
    def test_parses_ranges_all_and_removes_duplicates(self):
        self.assertEqual(parse_selection("1,3-4,3", 5), [0, 2, 3])
        self.assertEqual(parse_selection("all", 3), [0, 1, 2])
        self.assertEqual(parse_selection("*", 2), [0, 1])

    def test_rejects_invalid_selection(self):
        with self.assertRaises(ValueError):
            parse_selection("0", 3)
        with self.assertRaises(ValueError):
            parse_selection("4", 3)
        with self.assertRaises(ValueError):
            parse_selection("3-1", 3)

    def test_builds_topic_jobs_like_legacy_sidecart(self):
        chats = parse_chats_json(SAMPLE)
        jobs = build_export_jobs(
            chats,
            selected_chat_indices=[0, 1],
            topic_selections={20: [0, 1]},
        )
        self.assertEqual(len(jobs), 3)
        self.assertIsNone(jobs[0].topic_id)
        self.assertEqual([jobs[1].topic_id, jobs[2].topic_id], [101, 102])

    def test_forum_requires_topic_selection(self):
        chats = parse_chats_json(SAMPLE)
        with self.assertRaises(ValueError):
            build_export_jobs(chats, selected_chat_indices=[1], topic_selections={})


class SafeComponentTests(unittest.TestCase):
    def test_replaces_windows_forbidden_characters(self):
        value = safe_component('A<B>: "C"/D\\E|F?G*')
        for char in '<>:"/\\|?*':
            self.assertNotIn(char, value)
        self.assertTrue(value)

    def test_handles_reserved_names_and_trailing_dots(self):
        self.assertNotEqual(safe_component("CON"), "CON")
        self.assertEqual(safe_component("name...   "), "name")

    def test_limits_component_length(self):
        self.assertEqual(len(safe_component("x" * 300, max_length=80)), 80)


class WizardCliTests(unittest.TestCase):
    def test_parser_exposes_interactive_wizard(self):
        from pathlib import Path
        from tdl_companionwulf import cli

        args = cli.build_parser().parse_args(
            ["wizard", "--dir", "downloads", "--media", "audio,video", "--takeout"]
        )
        self.assertEqual(args.command, "wizard")
        self.assertEqual(args.dir, Path("downloads"))
        self.assertEqual(args.media, "audio,video")
        self.assertTrue(args.takeout)


class WizardEndToEndTests(unittest.TestCase):
    @unittest.skipIf(os.name == "nt", "POSIX fake executable launcher")
    def test_fake_tdl_runs_chat_topic_export_and_download_flow(self):
        import stat
        import subprocess
        import sys
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            fake = root / "tdl"
            log = root / "calls.log"
            output = root / "out"
            fake_code = f'''#!/usr/bin/env python3
import json, pathlib, sys
args = sys.argv[1:]
pathlib.Path({str(log)!r}).open("a", encoding="utf-8").write(json.dumps(args) + "\\n")
if "chat" in args and "ls" in args:
    print({SAMPLE!r})
elif "chat" in args and "export" in args:
    target = pathlib.Path(args[args.index("-o") + 1])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('{{"messages":[]}}', encoding="utf-8")
sys.exit(0)
'''
            fake.write_text(fake_code, encoding="utf-8")
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)

            env = os.environ.copy()
            env["PATH"] = str(root) + os.pathsep + env.get("PATH", "")
            env["XDG_STATE_HOME"] = str(root / "state")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tdl_companionwulf.cli",
                    "wizard",
                    "--dir",
                    str(output),
                    "--namespace",
                    "smoke",
                    "--no-auto-auth",
                    "--media",
                    "audio",
                ],
                input="all\nall\n",
                text=True,
                capture_output=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(len(list(output.rglob("*_tdl-export.json"))), 3)
            self.assertEqual(len(log.read_text(encoding="utf-8").splitlines()), 7)


class WizardAuthOptionTests(unittest.TestCase):
    def test_wizard_can_disable_automatic_authentication(self):
        from tdl_companionwulf import cli

        args = cli.build_parser().parse_args(["wizard", "--no-auto-auth"])
        self.assertTrue(args.no_auto_auth)
