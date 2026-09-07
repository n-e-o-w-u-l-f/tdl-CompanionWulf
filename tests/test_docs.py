import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README_CODES = (
    "de", "fr", "es", "it", "pt", "nl", "pl", "cs", "sk", "hu", "ro",
    "tr", "ru", "uk", "bg", "el", "sv", "da", "no", "fi",
)


class DocumentationTests(unittest.TestCase):
    def test_all_supported_readme_translations_exist(self):
        expected = {ROOT / "README.md", ROOT / "README.TRANSLATIONS.md"}
        expected.update(ROOT / f"README.{code}.md" for code in README_CODES)
        missing = sorted(str(path.relative_to(ROOT)) for path in expected if not path.is_file())
        self.assertEqual(missing, [])

    def test_gitbook_entrypoints_exist(self):
        self.assertTrue((ROOT / ".gitbook.yaml").is_file())
        self.assertTrue((ROOT / "SUMMARY.md").is_file())
        self.assertIn("README.md", (ROOT / ".gitbook.yaml").read_text(encoding="utf-8"))
        self.assertIn("SUMMARY.md", (ROOT / ".gitbook.yaml").read_text(encoding="utf-8"))

    def test_relative_markdown_links_resolve(self):
        pattern = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
        failures = []
        for document in ROOT.rglob("*.md"):
            if ".git" in document.parts:
                continue
            text = document.read_text(encoding="utf-8")
            for raw in pattern.findall(text):
                target = raw.strip().split()[0].strip("<>\"")
                if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                target = target.split("#", 1)[0]
                if not target:
                    continue
                resolved = (document.parent / target).resolve()
                if not resolved.exists():
                    failures.append(f"{document.relative_to(ROOT)} -> {target}")
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
