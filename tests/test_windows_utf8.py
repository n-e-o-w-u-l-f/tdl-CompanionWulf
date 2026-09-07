import json
import subprocess
import sys
import unittest

from tdl_companionwulf import cli, cli_0_6
from tdl_companionwulf.entrypoint import Utf8SubprocessProxy


class WindowsUtf8CaptureTests(unittest.TestCase):
    def setUp(self):
        self.proxy = Utf8SubprocessProxy()

    def test_utf8_capture_handles_cp1252_undefined_continuation_byte(self):
        script = (
            "import sys; "
            "sys.stdout.buffer.write('{\"visible_name\":\"ѝ\"}\\n'.encode('utf-8'))"
        )
        result = self.proxy.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["visible_name"], "ѝ")

    def test_invalid_utf8_is_replaced_instead_of_crashing_reader_thread(self):
        result = self.proxy.run(
            [
                sys.executable,
                "-c",
                "import sys; sys.stdout.buffer.write(b'bad:\\xff')",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "bad:�")

    def test_entrypoint_installs_proxy_for_current_and_legacy_cli(self):
        self.assertIsInstance(cli.subprocess, Utf8SubprocessProxy)
        self.assertIsInstance(cli_0_6.subprocess, Utf8SubprocessProxy)
        self.assertIs(cli.subprocess, cli_0_6.subprocess)

    def test_binary_capture_remains_bytes(self):
        result = self.proxy.run(
            [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'abc')"],
            capture_output=True,
        )
        self.assertEqual(result.stdout, b"abc")


if __name__ == "__main__":
    unittest.main()
