import json
import tempfile
import unittest
from pathlib import Path

from tdl_companionwulf.collisions import (
    extract_export_media,
    prepare_existing_files,
    read_export_media,
    safe_filename,
    unique_renamed_path,
)


class FilenameCollisionTests(unittest.TestCase):
    def test_unique_renamed_path_skips_existing_suffixes(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            target = root / "track.mp3"
            (root / "track (1).mp3").write_bytes(b"old")
            self.assertEqual(unique_renamed_path(target), root / "track (2).mp3")

    def test_safe_filename_preserves_extension_and_windows_rules(self):
        self.assertEqual(safe_filename('A<B>.mp3'), "A_B_.mp3")
        self.assertEqual(safe_filename("CON.txt"), "_CON.txt")
        value = safe_filename("x" * 300 + ".flac", max_length=80)
        self.assertEqual(len(value), 80)
        self.assertTrue(value.endswith(".flac"))


class ExportMediaTests(unittest.TestCase):
    def test_extracts_legacy_flat_name_and_size(self):
        media = extract_export_media({"file_name": "song.mp3", "file_size": 123})
        self.assertEqual((media.name, media.size), ("song.mp3", 123))

    def test_extracts_current_file_without_inventing_size(self):
        media = extract_export_media({"file": "report.pdf"})
        self.assertEqual(media.name, "report.pdf")
        self.assertIsNone(media.size)

    def test_extracts_nested_media_name_and_size(self):
        media = extract_export_media({"Media": {"Name": "clip.mp4", "Size": "456"}})
        self.assertEqual((media.name, media.size), ("clip.mp4", 456))

    def test_reads_supported_export_containers(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            for key in (None, "messages", "data", "result"):
                path = root / f"{key or 'array'}.json"
                messages = [{"file_name": "x.bin", "file_size": 4}]
                payload = messages if key is None else {key: messages}
                path.write_text(json.dumps(payload), encoding="utf-8")
                media = read_export_media(path)
                self.assertEqual([(item.name, item.size) for item in media], [("x.bin", 4)])


class PrepareExistingTests(unittest.TestCase):
    def _export(self, root: Path, message: dict) -> Path:
        path = root / "export.json"
        path.write_text(json.dumps([message]), encoding="utf-8")
        return path

    def test_same_size_is_preserved(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            target = root / "song.mp3"
            target.write_bytes(b"1234")
            summary = prepare_existing_files(
                self._export(root, {"file_name": "song.mp3", "file_size": 4}), root
            )
            self.assertTrue(target.is_file())
            self.assertFalse((root / "song (1).mp3").exists())
            self.assertEqual((summary.checked, summary.same, summary.renamed), (1, 1, 0))

    def test_different_size_is_renamed_before_download(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            target = root / "song.mp3"
            target.write_bytes(b"old")
            summary = prepare_existing_files(
                self._export(root, {"file_name": "song.mp3", "file_size": 10}), root
            )
            self.assertFalse(target.exists())
            renamed = root / "song (1).mp3"
            self.assertEqual(renamed.read_bytes(), b"old")
            self.assertEqual((summary.checked, summary.same, summary.renamed), (1, 0, 1))

    def test_unknown_remote_size_does_not_rename(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            target = root / "report.pdf"
            target.write_bytes(b"existing")
            summary = prepare_existing_files(
                self._export(root, {"file": "report.pdf"}), root
            )
            self.assertTrue(target.is_file())
            self.assertFalse((root / "report (1).pdf").exists())
            self.assertEqual(summary.unknown, 1)
            self.assertEqual(summary.renamed, 0)

    def test_missing_target_is_not_counted_as_collision(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            summary = prepare_existing_files(
                self._export(root, {"file_name": "new.bin", "file_size": 3}), root
            )
            self.assertEqual(summary.checked, 0)


class HashCollisionTests(unittest.TestCase):
    def test_extracts_remote_sha256_when_present(self):
        digest = "a" * 64
        media = extract_export_media(
            {"file_name": "song.mp3", "file_size": 4, "sha256": digest}
        )
        self.assertEqual(media.sha256, digest)

    def test_matching_remote_hash_preserves_same_file(self):
        import hashlib

        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            target = root / "song.mp3"
            target.write_bytes(b"same")
            digest = hashlib.sha256(b"same").hexdigest()
            export = root / "export.json"
            export.write_text(
                json.dumps([{"file_name": "song.mp3", "file_size": 4, "sha256": digest}]),
                encoding="utf-8",
            )
            summary = prepare_existing_files(export, root)
            self.assertTrue(target.is_file())
            self.assertEqual(summary.same, 1)
            self.assertEqual(summary.renamed, 0)

    def test_different_remote_hash_renames_even_when_size_matches(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            target = root / "song.mp3"
            target.write_bytes(b"same")
            export = root / "export.json"
            export.write_text(
                json.dumps([{"file_name": "song.mp3", "file_size": 4, "sha256": "0" * 64}]),
                encoding="utf-8",
            )
            summary = prepare_existing_files(export, root)
            self.assertFalse(target.exists())
            self.assertEqual((root / "song (1).mp3").read_bytes(), b"same")
            self.assertEqual(summary.renamed, 1)
