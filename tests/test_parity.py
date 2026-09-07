import os
import tempfile
import unittest
from pathlib import Path

from tdl_companionwulf import cli
from tdl_companionwulf.collisions import prepare_existing_files


class ParityTests(unittest.TestCase):
    def test_cli_exposes_sidecart_parity_flags(self):
        args = cli.build_parser().parse_args([
            "wizard", "--tdl-path", "/tmp/tdl", "--language", "fr",
            "--max-filename-length", "120", "--existing-file-comparison", "hash",
            "--dry-run",
        ])
        self.assertEqual(args.max_filename_length, 120)
        self.assertEqual(args.existing_file_comparison, "hash")
        self.assertTrue(args.what_if_download)

    def test_global_language_survives_subparser_defaults(self):
        args = cli.build_parser().parse_args([
            "--language", "fr", "wizard", "--media", "audio",
        ])
        self.assertEqual(args.language, "fr")

    def test_parallel_namespace_contains_pid(self):
        value = cli.new_parallel_namespace()
        self.assertTrue(value.startswith("companion_"))
        self.assertIn(str(os.getpid()), value)

    def test_size_comparison_preserves_equal_size(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            target = root / "song.mp3"
            target.write_bytes(b"1234")
            export = root / "export.json"
            export.write_text('[{"file":"song.mp3","size":4,"sha256":"' + '0'*64 + '"}]')
            summary = prepare_existing_files(export, root, comparison="size")
            self.assertEqual(summary.same, 1)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
