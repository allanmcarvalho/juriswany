from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "juriswany"


class LocalCLI(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="juriswany-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.repo = self.base / "origem"
        self.package = self.repo / "skills" / "juriswany"
        (self.package / "scripts").mkdir(parents=True)
        shutil.copyfile(SOURCE / "scripts" / "local.py", self.package / "scripts" / "local.py")
        shutil.copyfile(SOURCE / "manifest.json", self.package / "manifest.json")
        (self.package / "SKILL.md").write_text("---\nname: juriswany\ndescription: Exemplo fictício.\n---\n", encoding="utf-8")
        (self.repo / "LICENSE").write_text("MIT License\nFixture fictícia de teste.\n", encoding="utf-8")
        (self.repo / "README.md").write_text("Fixture.\n", encoding="utf-8")
        self.environment = os.environ.copy()
        self.environment.update({"XDG_CONFIG_HOME": str(self.base / "config"),
                                 "XDG_CACHE_HOME": str(self.base / "cache"),
                                 "GIT_CONFIG_GLOBAL": os.devnull,
                                 "GIT_CONFIG_SYSTEM": os.devnull})
        self.codex = self.base / "operador" / ".agents" / "skills" / "juriswany"
        self.claude = self.base / "operador" / ".claude" / "skills" / "juriswany"

    def cli(self, *arguments, package=None, success=True):
        script = (package or self.package) / "scripts" / "local.py"
        result = subprocess.run([sys.executable, str(script), *arguments],
                                env=self.environment, capture_output=True, text=True,
                                timeout=30)
        self.assertNotIn("Traceback", result.stderr)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return json.loads(result.stderr)

    def install(self, destination=None, package=None, host="codex", success=True):
        return self.cli("instalar", host, "--destino", str(destination or self.codex),
                        package=package, success=success)

    def git(self, *arguments, cwd=None):
        return subprocess.run(["git", "-c", "user.name=Operador fictício",
                               "-c", "user.email=fixture@example.invalid", *arguments],
                              cwd=cwd or self.repo, env=self.environment, capture_output=True,
                              text=True, check=True, timeout=30).stdout.strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-m", "Fixture de comportamento")
        return self.git("rev-parse", "HEAD")

    def initialize_git(self):
        self.git("init", "-b", "main")
        return self.commit()

    def update(self, package=None, force=True, repository=None):
        arguments = ["atualizacoes", "--repositorio", str(repository or self.repo)]
        if force:
            arguments.append("--forcar")
        return self.cli(*arguments, package=package or self.codex)

    def profile_file(self):
        return self.base / "config" / "juriswany" / "perfil.json"

    def test_install_idempotent_license_both_hosts_and_shared_profile(self):
        first = self.install()
        self.assertEqual(first["estado"], "instalado")
        self.assertEqual(first["procedencia"]["tipo"], "sem_procedencia")
        before = {path.relative_to(self.codex): (path.read_bytes(), path.stat().st_mtime_ns)
                  for path in self.codex.rglob("*") if path.is_file()}
        self.assertEqual(self.install()["estado"], "ja_instalado")
        after = {path.relative_to(self.codex): (path.read_bytes(), path.stat().st_mtime_ns)
                 for path in self.codex.rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        self.assertEqual((self.codex / "LICENSE").read_bytes(), (self.repo / "LICENSE").read_bytes())
        self.cli("perfil", "definir", "--nome", "Lia", "--tratamento", "Dra.", package=self.codex)
        self.install(self.claude, package=self.codex, host="claude")
        self.assertEqual(self.cli("perfil", "mostrar", package=self.claude)["perfil"]["nome"], "Lia")
        (self.package / "SKILL.md").write_text("Nova instrução fictícia.\n", encoding="utf-8")
        self.assertEqual(self.install()["estado"], "substituido")
        self.assertEqual(self.cli("perfil", "mostrar", package=self.codex)["perfil"]["tratamento"], "Dra.")
        self.assertFalse((self.codex / "perfil.json").exists())

    def test_reading_defaults_does_not_create_profile_and_export_is_reusable(self):
        result = self.cli("perfil", "mostrar")["perfil"]
        self.assertEqual(result, {"formato": 1, "revisao": 0, "resposta": "curta",
                                  "execucao": "economica", "consulta": "semanal"})
        self.assertFalse(self.profile_file().parent.exists())
        self.cli("perfil", "definir", "--nome", "Lia", "--resposta", "detalhada")
        self.cli("perfil", "definir", "--execucao", "aprofundada")
        profile = self.cli("perfil", "mostrar")["perfil"]
        self.assertEqual(profile["nome"], "Lia")
        self.assertEqual(profile["resposta"], "detalhada")
        self.assertEqual(profile["revisao"], 2)
        self.assertEqual(stat.S_IMODE(self.profile_file().stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.profile_file().parent.stat().st_mode), 0o700)
        exported = self.cli("perfil", "exportar")["texto"]
        self.assertIn("Lia", exported)
        self.assertIn("detalhada", exported)
        self.assertIn("não garante memória", exported)

    def test_profile_concurrent_partial_changes_are_not_lost(self):
        changes = [("--nome", "Lia"), ("--tratamento", "Dra."),
                   ("--resposta", "detalhada"), ("--execucao", "equilibrada"),
                   ("--consulta", "diaria")]
        with ThreadPoolExecutor(max_workers=5) as workers:
            list(workers.map(lambda pair: self.cli("perfil", "definir", *pair), changes))
        profile = self.cli("perfil", "mostrar")["perfil"]
        self.assertEqual(profile["revisao"], 5)
        for flag, expected in changes:
            self.assertEqual(profile[flag[2:]], expected)

    def test_simultaneous_installs_converge_without_replacing_files(self):
        with ThreadPoolExecutor(max_workers=3) as workers:
            results = list(workers.map(lambda _: self.install(), range(3)))
        self.assertEqual(sorted(item["estado"] for item in results),
                         ["instalado", "ja_instalado", "ja_instalado"])
        self.assertEqual((self.codex / "SKILL.md").read_bytes(),
                         (self.package / "SKILL.md").read_bytes())

    def test_invalid_input_and_invalid_existing_profile_are_preserved(self):
        self.cli("perfil", "definir", "--nome", "Lia")
        before = self.profile_file().read_bytes()
        for arguments in (("--nome", ""), ("--tratamento", "a" * 41),
                          ("--nome", "Lia\nOutra"), ("--execucao", "paga"), ()):
            with self.subTest(arguments=arguments):
                self.cli("perfil", "definir", *arguments, success=False)
                self.assertEqual(self.profile_file().read_bytes(), before)
        for content in ("{", '{"formato":2}',
                        '{"formato":1,"revisao":false,"resposta":"curta","execucao":"economica","consulta":"semanal"}'):
            self.profile_file().write_text(content, encoding="utf-8")
            self.cli("perfil", "definir", "--nome", "Outro", success=False)
            self.assertEqual(self.profile_file().read_text(encoding="utf-8"), content)

    def test_unknown_modified_extra_and_symlink_installations_are_preserved(self):
        self.codex.mkdir(parents=True)
        precious = self.codex / "anotacao.txt"
        precious.write_text("Não perder.\n", encoding="utf-8")
        self.install(success=False)
        self.assertEqual(precious.read_text(encoding="utf-8"), "Não perder.\n")
        shutil.rmtree(self.codex)
        self.install()
        original = (self.codex / "SKILL.md").read_bytes()
        (self.codex / "SKILL.md").write_text("Edição local.\n", encoding="utf-8")
        self.install(success=False)
        self.assertEqual((self.codex / "SKILL.md").read_text(encoding="utf-8"), "Edição local.\n")
        (self.codex / "SKILL.md").write_bytes(original)
        precious.write_text("Extra.\n", encoding="utf-8")
        self.install(success=False)
        self.assertTrue(precious.exists())
        precious.unlink()
        (self.codex / "pasta-extra").mkdir()
        self.install(success=False)
        self.assertTrue((self.codex / "pasta-extra").is_dir())
        shutil.rmtree(self.codex)
        target = self.base / "outro"
        target.mkdir()
        self.codex.symlink_to(target, target_is_directory=True)
        self.install(success=False)
        self.assertTrue(self.codex.is_symlink())
        self.assertEqual(list(target.iterdir()), [])

    def test_forged_marker_paths_and_symlink_content_are_rejected(self):
        self.install()
        marker = self.codex / ".juriswany-install.json"
        original = json.loads(marker.read_text(encoding="utf-8"))
        for malicious in ("/tmp/fora", "../fora", "scripts/../../fora", "scripts//fora", "./fora", "C:\\fora"):
            with self.subTest(path=malicious):
                forged = dict(original, arquivos=dict(original["arquivos"]))
                forged["arquivos"][malicious] = "0" * 64
                marker.write_text(json.dumps(forged), encoding="utf-8")
                self.install(success=False)
                self.assertIn(malicious, marker.read_text(encoding="utf-8").replace("\\\\", "\\"))
        marker.write_text(json.dumps(original), encoding="utf-8")
        outside = self.base / "segredo.txt"
        outside.write_text("Fora do pacote.", encoding="utf-8")
        (self.codex / "SKILL.md").unlink()
        (self.codex / "SKILL.md").symlink_to(outside)
        self.install(success=False)
        self.assertEqual(outside.read_text(encoding="utf-8"), "Fora do pacote.")

    def test_replacement_keeps_backup_and_recovers_interrupted_publication(self):
        self.install()
        previous = (self.codex / "SKILL.md").read_bytes()
        (self.package / "SKILL.md").write_text("Nova versão.\n", encoding="utf-8")
        result = self.install()
        backup = Path(result["backup"])
        self.assertEqual((backup / "SKILL.md").read_bytes(), previous)
        staging = self.codex.with_name(".juriswany.stage-interrompida")
        shutil.copytree(self.codex, staging)
        shutil.rmtree(self.codex)
        recovered = self.install()
        self.assertTrue(recovered["recuperado"])
        self.assertEqual((self.codex / "SKILL.md").read_text(encoding="utf-8"), "Nova versão.\n")
        self.assertTrue(staging.exists())

    def test_retry_after_partial_backup_removal_preserves_abandoned_content(self):
        self.install()
        (self.package / "SKILL.md").write_text("Versão dois.\n", encoding="utf-8")
        self.install()
        (self.package / "SKILL.md").write_text("Versão três.\n", encoding="utf-8")
        wrapper = self.base / "interromper.py"
        wrapper.write_text(
            "import runpy, shutil, sys\n"
            "from pathlib import Path\n"
            "original = shutil.rmtree\n"
            "def interromper(path, *args, **kwargs):\n"
            "    root = Path(path)\n"
            "    if root.name == '.juriswany.backup' or root.name.startswith('.juriswany.discard-'):\n"
            "        (root / 'SKILL.md').unlink()\n"
            "        raise OSError('Interrupção simulada durante remoção.')\n"
            "    return original(path, *args, **kwargs)\n"
            "shutil.rmtree = interromper\n"
            "script = sys.argv.pop(1)\n"
            "runpy.run_path(script, run_name='__main__')\n",
            encoding="utf-8",
        )
        failed = subprocess.run(
            [sys.executable, str(wrapper), str(self.package / "scripts" / "local.py"),
             "instalar", "codex", "--destino", str(self.codex)],
            env=self.environment, capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertNotIn("Traceback", failed.stderr)
        self.assertIn("Interrupção simulada", json.loads(failed.stderr)["mensagem"])
        self.assertEqual((self.codex / "SKILL.md").read_text(encoding="utf-8"), "Versão dois.\n")
        abandoned, = [path for path in self.codex.parent.iterdir()
                      if path.is_dir() and path != self.codex]
        remaining = {path.relative_to(abandoned): path.read_bytes()
                     for path in abandoned.rglob("*") if path.is_file()}
        self.assertNotIn(Path("SKILL.md"), remaining)
        self.assertIn(Path(".juriswany-install.json"), remaining)
        self.assertEqual(self.install()["estado"], "substituido")
        self.assertEqual((self.codex / "SKILL.md").read_text(encoding="utf-8"), "Versão três.\n")
        self.assertEqual({path.relative_to(abandoned): path.read_bytes()
                          for path in abandoned.rglob("*") if path.is_file()}, remaining)

    def test_interrupted_staging_does_not_block_install_or_delete_unknown_content(self):
        staging = self.codex.with_name(".juriswany.stage-interrompida")
        staging.mkdir(parents=True)
        (staging / "nao-apagar.txt").write_text("Desconhecido.", encoding="utf-8")
        self.assertEqual(self.install()["estado"], "instalado")
        self.assertEqual(self.install()["estado"], "ja_instalado")
        self.assertTrue((staging / "nao-apagar.txt").exists())

    def test_generated_junk_is_not_installed_and_dirty_source_has_no_provenance(self):
        self.initialize_git()
        (self.package / "__pycache__").mkdir()
        (self.package / "__pycache__" / "local.pyc").write_bytes(b"cache")
        (self.package / ".DS_Store").write_bytes(b"finder")
        self.assertEqual(self.install()["procedencia"]["tipo"], "git")
        self.assertFalse((self.codex / "__pycache__").exists())
        self.assertFalse((self.codex / ".DS_Store").exists())
        (self.package / "SKILL.md").write_text("Mudança ainda não revisada.\n", encoding="utf-8")
        self.assertEqual(self.install()["procedencia"]["tipo"], "sem_procedencia")
        self.assertEqual(self.update()["estado"], "sem_procedencia")
        self.assertFalse((self.base / "cache").exists())

    def test_untracked_source_file_prevents_git_provenance(self):
        self.initialize_git()
        (self.package / "extra.txt").write_text("Conteúdo local.", encoding="utf-8")
        self.assertEqual(self.install()["procedencia"]["tipo"], "sem_procedencia")
        self.assertTrue((self.codex / "extra.txt").exists())

    def test_empty_untracked_directory_prevents_verified_git_provenance(self):
        self.initialize_git()
        (self.package / "vazia").mkdir()
        self.assertEqual(self.install()["procedencia"]["tipo"], "sem_procedencia")

    def test_git_provenance_survives_managed_copy_for_second_host(self):
        commit = self.initialize_git()
        first = self.install()
        self.assertEqual(first["procedencia"]["commit"], commit)
        second = self.install(self.claude, package=self.codex, host="claude")
        self.assertEqual(second["procedencia"], first["procedencia"])
        self.assertEqual(self.update(package=self.claude)["estado"], "atual")

    def test_reinstall_adopts_new_git_provenance_without_replacing_package_files(self):
        self.install()
        before = {path.relative_to(self.codex): (path.read_bytes(), path.stat().st_mtime_ns)
                  for path in self.codex.rglob("*")
                  if path.is_file() and path.name != ".juriswany-install.json"}
        commit = self.initialize_git()
        result = self.install()
        self.assertEqual(result["estado"], "ja_instalado")
        self.assertEqual(result["procedencia"]["tipo"], "git")
        self.assertEqual(result["procedencia"]["commit"], commit)
        self.assertEqual({path.relative_to(self.codex): (path.read_bytes(), path.stat().st_mtime_ns)
                          for path in self.codex.rglob("*")
                          if path.is_file() and path.name != ".juriswany-install.json"}, before)
        self.assertEqual(self.update()["estado"], "atual")

    def test_reinstall_refreshes_changed_git_tree_with_identical_file_bytes(self):
        self.initialize_git()
        self.install()
        before = {path.relative_to(self.codex): (path.read_bytes(), path.stat().st_mtime_ns)
                  for path in self.codex.rglob("*")
                  if path.is_file() and path.name != ".juriswany-install.json"}
        self.git("config", "core.filemode", "true")
        (self.package / "SKILL.md").chmod(0o755)
        commit = self.commit()
        self.assertEqual(self.update()["estado"], "diferente")
        result = self.install()
        self.assertEqual(result["estado"], "ja_instalado")
        self.assertEqual(result["procedencia"]["commit"], commit)
        self.assertEqual({path.relative_to(self.codex): (path.read_bytes(), path.stat().st_mtime_ns)
                          for path in self.codex.rglob("*")
                          if path.is_file() and path.name != ".juriswany-install.json"}, before)
        self.assertEqual(self.update()["estado"], "atual")

    def test_reinstall_preserves_verified_provenance_when_source_is_unverified(self):
        self.initialize_git()
        first = self.install()
        marker = self.codex / ".juriswany-install.json"
        before = marker.read_bytes(), marker.stat().st_mtime_ns
        (self.package / "vazia").mkdir()
        self.assertEqual(self.install()["procedencia"], first["procedencia"])
        self.assertEqual((marker.read_bytes(), marker.stat().st_mtime_ns), before)
        self.assertEqual(self.update()["estado"], "atual")

    def test_update_compares_package_tree_ignores_readme_and_never_installs(self):
        origin = self.initialize_git()
        self.install()
        installed = (self.codex / "SKILL.md").read_bytes()
        self.assertEqual(self.update()["estado"], "atual")
        (self.repo / "README.md").write_text("Só a apresentação mudou.\n", encoding="utf-8")
        readme_commit = self.commit()
        marker = self.codex / ".juriswany-install.json"
        marker_before = (marker.read_bytes(), marker.stat().st_mtime_ns)
        self.assertEqual(self.install()["estado"], "ja_instalado")
        self.assertEqual((marker.read_bytes(), marker.stat().st_mtime_ns), marker_before)
        result = self.update()
        self.assertEqual(result["estado"], "atual")
        self.assertEqual(result["commit_origem"], origin)
        self.assertEqual(result["commit_remoto"], readme_commit)
        (self.package / "SKILL.md").write_text("Mudou o pacote.\n", encoding="utf-8")
        latest = self.commit()
        different = self.update()
        self.assertEqual(different["estado"], "diferente")
        self.assertEqual(different["commit_remoto"], latest)
        self.assertNotEqual(different["arvore_origem"], different["arvore_remota"])
        self.assertEqual((self.codex / "SKILL.md").read_bytes(), installed)
        self.assertNotIn("comparacao", different)

    def test_update_cache_manual_mode_and_offline_are_informative(self):
        self.initialize_git()
        self.install()
        self.cli("perfil", "definir", "--nome", "Pessoa fictícia", "--consulta", "semanal")
        self.assertFalse(self.update(force=False)["cache"])
        (self.package / "SKILL.md").write_text("Mudança remota.\n", encoding="utf-8")
        self.commit()
        cached = self.update(force=False)
        self.assertTrue(cached["cache"])
        self.assertEqual(cached["estado"], "atual")
        self.assertEqual(self.update()["estado"], "diferente")
        self.cli("perfil", "definir", "--consulta", "manual")
        disabled = self.update(force=False)
        self.assertEqual(disabled["motivo"], "consulta_automatica_desabilitada")
        self.assertEqual(self.update()["estado"], "diferente")
        offline = self.update(repository=self.base / "sem-remoto")
        self.assertEqual(offline["estado"], "indisponivel")
        for path in (self.base / "cache").rglob("*.json"):
            self.assertNotIn("Pessoa fictícia", path.read_text(encoding="utf-8"))

    def test_update_detects_license_only_change_and_reinstall_refreshes_cache(self):
        self.initialize_git()
        self.install()
        self.assertEqual(self.update(force=False)["estado"], "atual")
        original = (self.codex / "LICENSE").read_bytes()
        (self.repo / "LICENSE").write_text("MIT License\nNova licença fictícia.\n", encoding="utf-8")
        self.commit()
        different = self.update()
        self.assertEqual(different["estado"], "diferente")
        self.assertEqual(different["arvore_origem"], different["arvore_remota"])
        self.assertNotEqual(different["licenca_origem"], different["licenca_remota"])
        self.assertEqual((self.codex / "LICENSE").read_bytes(), original)
        self.assertEqual(self.install()["estado"], "substituido")
        current = self.update(force=False)
        self.assertEqual(current["estado"], "atual")
        self.assertFalse(current["cache"])
        self.assertEqual(current["licenca_origem"], current["licenca_remota"])

    def test_update_cache_identity_includes_distributed_license(self):
        self.initialize_git()
        self.install()
        self.assertEqual(self.update(force=False)["estado"], "atual")
        license_path = self.codex / "LICENSE"
        license_path.write_text("MIT License\nOutra distribuição fictícia.\n", encoding="utf-8")
        marker_path = self.codex / ".juriswany-install.json"
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        marker["arquivos"]["LICENSE"] = hashlib.sha256(license_path.read_bytes()).hexdigest()
        marker_path.write_text(json.dumps(marker), encoding="utf-8")
        result = self.update(force=False)
        self.assertFalse(result["cache"])
        self.assertEqual(result["estado"], "diferente")


if __name__ == "__main__":
    unittest.main()
