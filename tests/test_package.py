from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "skills" / "juriswany"


class PortablePackage(unittest.TestCase):
    def test_distributed_license_matches_repository_license(self):
        self.assertEqual((PACKAGE / "LICENSE").read_bytes(), (ROOT / "LICENSE").read_bytes())

    def test_native_folder_copy_runs_and_installs_without_repository_root(self):
        with tempfile.TemporaryDirectory(prefix="juriswany-package-") as temporary:
            base = Path(temporary)
            source = base / "download" / "juriswany"
            shutil.copytree(PACKAGE, source, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            environment = os.environ.copy()
            environment.update({"XDG_CONFIG_HOME": str(base / "config"), "XDG_CACHE_HOME": str(base / "cache")})
            destination = base / "installed" / "juriswany"
            result = subprocess.run(
                [sys.executable, str(source / "scripts/local.py"), "instalar", "codex", "--destino", str(destination)],
                env=environment, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["estado"], "instalado")
            self.assertEqual((destination / "LICENSE").read_bytes(), (ROOT / "LICENSE").read_bytes())
            self.assertTrue((destination / "references/conversa.md").is_file())
            self.assertFalse((base / "config").exists())


if __name__ == "__main__":
    unittest.main()
