from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

import test_local


class ShortcutCLI(unittest.TestCase):
    cli = test_local.LocalCLI.cli
    install = test_local.LocalCLI.install

    def setUp(self):
        test_local.LocalCLI.setUp(self)
        shutil.copytree(test_local.SOURCE / "atalhos", self.package / "atalhos")

    def links(self):
        return sorted(self.codex.parent.glob("juriswany-*"))

    def test_shortcuts_follow_updates_reinstall_and_custom_destination(self):
        custom = self.codex.with_name("secretaria")
        first = self.install(custom)
        self.assertEqual(len(first["atalhos"]), 11)
        links = [Path(path) for path in first["atalhos"]]
        times = {link: link.lstat().st_mtime_ns for link in links}
        for link in links:
            self.assertFalse(Path(os.readlink(link)).is_absolute())
            self.assertEqual(link.resolve(), custom.resolve() / "atalhos" / link.name)
        self.assertEqual(self.install(custom)["estado"], "ja_instalado")
        self.assertEqual(times, {link: link.lstat().st_mtime_ns for link in links})
        source = self.package / "atalhos/juriswany-revisar/SKILL.md"
        source.write_text(source.read_text(encoding="utf-8") + "\nInstrução nova fictícia.\n", encoding="utf-8")
        self.assertEqual(self.install(custom)["estado"], "substituido")
        revised = custom.parent / "juriswany-revisar/SKILL.md"
        self.assertEqual(revised.read_bytes(), source.read_bytes())
        self.assertEqual(times, {link: link.lstat().st_mtime_ns for link in links})
        copied = self.install(self.claude, package=custom, host="claude")
        self.assertEqual(len(copied["atalhos"]), 11)
        self.assertEqual((self.claude.parent / "juriswany-revisar/SKILL.md").read_bytes(), source.read_bytes())

    def test_update_from_installation_without_shortcuts_preserves_profile(self):
        saved = self.base / "saved-shortcuts"
        (self.package / "atalhos").rename(saved)
        self.assertEqual(self.install()["atalhos"], [])
        self.cli("perfil", "definir", "--nome", "Lia", package=self.codex)
        profile = self.base / "config/juriswany/perfil.json"
        before = profile.read_bytes()
        saved.rename(self.package / "atalhos")
        updated = self.install()
        self.assertEqual(updated["estado"], "substituido")
        self.assertEqual(len(updated["atalhos"]), 11)
        self.assertEqual(profile.read_bytes(), before)
        self.assertEqual(updated["canal"], "dev")

    def test_reinstall_repairs_missing_links_without_rewriting_package(self):
        self.install()
        marker = self.codex / ".juriswany-install.json"
        before = (marker.read_bytes(), marker.stat().st_mtime_ns)
        (self.codex.parent / "juriswany-revisar").unlink()
        result = self.install(package=self.codex)
        self.assertEqual(result["estado"], "ja_instalado")
        self.assertTrue((self.codex.parent / "juriswany-revisar/SKILL.md").is_file())
        self.assertEqual((marker.read_bytes(), marker.stat().st_mtime_ns), before)

    def test_name_conflicts_preserve_foreign_paths_and_create_no_shortcuts(self):
        self.codex.parent.mkdir(parents=True)
        occupied = self.codex.parent / "juriswany-revisar"
        for kind in ("file", "directory", "symlink", "dangling"):
            with self.subTest(kind=kind):
                if kind == "file":
                    occupied.write_text("Preservar este arquivo.", encoding="utf-8")
                elif kind == "directory":
                    occupied.mkdir()
                    (occupied / "nota.txt").write_text("Preservar esta nota.", encoding="utf-8")
                else:
                    occupied.symlink_to(self.package if kind == "symlink" else self.base / "ausente")
                self.install(success=False)
                self.assertFalse(self.codex.exists())
                self.assertEqual(self.links(), [occupied])
                if occupied.is_symlink():
                    self.assertEqual(os.readlink(occupied), str(self.package if kind == "symlink" else self.base / "ausente"))
                    occupied.unlink()
                elif occupied.is_dir():
                    self.assertEqual((occupied / "nota.txt").read_text(encoding="utf-8"), "Preservar esta nota.")
                    shutil.rmtree(occupied)
                else:
                    self.assertEqual(occupied.read_text(encoding="utf-8"), "Preservar este arquivo.")
                    occupied.unlink()

    def test_name_conflict_preserves_existing_installation(self):
        self.install()
        marker = self.codex / ".juriswany-install.json"
        before = marker.read_bytes()
        link = self.codex.parent / "juriswany-revisar"
        link.unlink()
        link.write_text("Preservar.", encoding="utf-8")
        (self.package / "SKILL.md").write_text("Nova versão fictícia.\n", encoding="utf-8")
        self.install(success=False)
        self.assertEqual(marker.read_bytes(), before)
        self.assertEqual(link.read_text(encoding="utf-8"), "Preservar.")

    def test_copy_failure_removes_only_new_links_and_preserves_installation(self):
        self.install()
        marker = self.codex / ".juriswany-install.json"
        before = marker.read_bytes()
        missing = self.codex.parent / "juriswany-revisar"
        missing.unlink()
        existing = self.links()
        (self.package / "SKILL.md").write_text("Nova versão fictícia.\n", encoding="utf-8")
        wrapper = ("import runpy, sys; from unittest.mock import patch; "
                   "sys.argv = sys.argv[1:]; "
                   "\nwith patch('shutil.copyfile', side_effect=OSError('Falha fictícia')): "
                   "runpy.run_path(sys.argv[0], run_name='__main__')")
        result = subprocess.run([sys.executable, "-c", wrapper, str(self.package / "scripts/local.py"),
                                 "instalar", "codex", "--destino", str(self.codex)],
                                env=self.environment, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stderr)["estado"], "erro")
        self.assertEqual(marker.read_bytes(), before)
        self.assertFalse(missing.is_symlink())
        self.assertEqual(self.links(), existing)
        self.assertTrue(all((link / "SKILL.md").is_file() for link in existing))

    def test_simultaneous_installs_converge_with_readable_shortcuts(self):
        with ThreadPoolExecutor(max_workers=3) as workers:
            results = list(workers.map(lambda _: self.install(), range(3)))
        self.assertEqual(sorted(result["estado"] for result in results),
                         ["instalado", "ja_instalado", "ja_instalado"])
        self.assertEqual(len(self.links()), 11)
        self.assertTrue(all((link / "SKILL.md").is_file() for link in self.links()))


if __name__ == "__main__":
    unittest.main()
