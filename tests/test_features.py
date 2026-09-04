import unittest

from tdl_companionwulf.i18n import normalize_language
from tdl_companionwulf.tdl import TdlOptions, build_chat_list_command, build_download_command


class LanguageTests(unittest.TestCase):
    def test_normalizes_supported_system_locale(self):
        self.assertEqual(normalize_language("de_DE.UTF-8"), "de")
        self.assertEqual(normalize_language("fr-FR"), "fr")
        self.assertEqual(normalize_language("pt_BR"), "pt")

    def test_unknown_language_falls_back_to_english(self):
        self.assertEqual(normalize_language("xx_YY"), "en")


class TdlCommandTests(unittest.TestCase):
    def test_builds_chat_list_json_command(self):
        options = TdlOptions(namespace="family", limit=4, threads=8, delay=2, pool=3)
        command = build_chat_list_command("tdl", options, json_output=True)
        self.assertEqual(command[-4:], ["chat", "ls", "-o", "json"])
        self.assertIn("family", command)

    def test_builds_download_command_with_sidecart_flags(self):
        options = TdlOptions(
            namespace="family",
            limit=4,
            threads=10,
            delay=2,
            proxy="socks5://127.0.0.1:1080",
        )
        command = build_download_command(
            "tdl",
            options,
            urls=["https://t.me/example/1"],
            directory="downloads",
            include=["mp4", "mp3"],
            takeout=True,
            rewrite_ext=True,
            group=True,
        )
        self.assertIn("dl", command)
        self.assertIn("--skip-same", command)
        self.assertIn("--takeout", command)
        self.assertIn("--rewrite-ext", command)
        self.assertIn("--group", command)
        self.assertIn("mp4,mp3", command)

    def test_continue_and_restart_are_mutually_exclusive(self):
        with self.assertRaises(ValueError):
            build_download_command(
                "tdl",
                TdlOptions(),
                urls=["https://t.me/example/1"],
                directory="downloads",
                continue_download=True,
                restart_download=True,
            )


class CliSurfaceTests(unittest.TestCase):
    def test_run_parser_exposes_sidecart_transfer_options(self):
        from tdl_companionwulf import cli

        args = cli.build_parser().parse_args(
            [
                "run",
                "--namespace", "family",
                "--takeout",
                "--include", "mp4,mp3",
                "--group",
            ]
        )
        self.assertEqual(args.namespace, "family")
        self.assertTrue(args.takeout)
        self.assertEqual(args.include, "mp4,mp3")
        self.assertTrue(args.group)

    def test_parser_exposes_chats_and_config_commands(self):
        from tdl_companionwulf import cli

        chats = cli.build_parser().parse_args(["chats", "--json"])
        config = cli.build_parser().parse_args(["config", "set", "namespace", "family"])
        self.assertTrue(chats.json)
        self.assertEqual(config.config_command, "set")
        self.assertEqual(config.key, "namespace")
        self.assertEqual(config.value, "family")
