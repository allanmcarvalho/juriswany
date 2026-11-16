from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FragmentLibrary(unittest.TestCase):
    def check(self, root):
        return subprocess.run([sys.executable, str(root / "tests/check_fragmentos.py")],
                              capture_output=True, text=True, timeout=10)

    def test_repository_library_is_consistent(self):
        result = self.check(ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_incomplete_duplicate_and_broken_indexes_are_rejected(self):
        for defect in ("unindexed", "duplicate", "wrong-chapter", "missing-file", "missing-anchor"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory(prefix="juriswany-fragments-") as temporary:
                root = Path(temporary)
                shutil.copytree(ROOT / "docs/pesquisa", root / "docs/pesquisa")
                (root / "tests").mkdir()
                shutil.copyfile(ROOT / "tests/check_fragmentos.py", root / "tests/check_fragmentos.py")
                index = root / "docs/pesquisa/fragmentos.md"
                text = index.read_text(encoding="utf-8")
                if defect == "unindexed":
                    text = text.replace("F01, F12", "F12") + "\nVeja também F01.\n"
                elif defect == "duplicate":
                    text = text.replace("F01, F12", "F01, F01, F12")
                elif defect == "wrong-chapter":
                    text = text.replace("F01, F12", "F17, F12").replace("F17 a F22", "F01, F18 a F22")
                elif defect == "missing-file":
                    text = text.replace("fragmentos/enderecamento.md", "fragmentos/ausente.md")
                else:
                    text = text.replace("fragmentos/enderecamento.md", "fragmentos/enderecamento.md#ausente")
                index.write_text(text, encoding="utf-8")
                result = self.check(root)
                self.assertNotEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
