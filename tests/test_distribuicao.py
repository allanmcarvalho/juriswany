"""Contrato público da CLI com Git real e HTTP restrito ao loopback."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import threading
import time
import unittest

import test_local


class DistributionCLI(unittest.TestCase):
    setUp = test_local.LocalCLI.setUp
    cli = test_local.LocalCLI.cli
    git = test_local.LocalCLI.git
    commit = test_local.LocalCLI.commit
    initialize_git = test_local.LocalCLI.initialize_git
    profile_file = test_local.LocalCLI.profile_file

    def release_source(self):
        shutil.copyfile(self.repo / "LICENSE", self.package / "LICENSE")
        manifest = self.package / "manifest.json"
        metadata = json.loads(manifest.read_text(encoding="utf-8"))
        metadata["versao"] = "0.2.0"
        manifest.write_text(json.dumps(metadata), encoding="utf-8")
        commit = self.initialize_git()
        self.git("tag", "v0.2.0")
        return commit

    def publish(self, tag="v0.3.0"):
        (self.package / "SKILL.md").write_text("Nova versão fictícia.\n", encoding="utf-8")
        manifest = self.package / "manifest.json"
        metadata = json.loads(manifest.read_text(encoding="utf-8"))
        metadata["versao"] = tag[1:]
        manifest.write_text(json.dumps(metadata), encoding="utf-8")
        commit = self.commit()
        self.git("tag", tag)
        return commit

    def native_copy(self):
        native = self.base / "download-nativo" / "juriswany"
        shutil.copytree(self.package, native)
        return native

    def install(self, *flags, package=None, success=True):
        return self.cli("instalar", "codex", "--destino", str(self.codex), *flags,
                        package=package, success=success)

    def stable(self, *flags, package=None, commit=None, success=True):
        args = ["--canal", "stable", "--release", "v0.2.0"]
        if commit:
            args += ["--origem-git", str(self.repo), "--commit", commit]
        return self.install(*args, *flags, package=package, success=success)

    @contextmanager
    def api(self, tag="v0.2.0", status=200, changes=None, raw=None, delay=0, redirect=None):
        payload = {"draft": False, "prerelease": False, "tag_name": tag,
                   "published_at": "2026-11-14T12:00:00Z",
                   "html_url": "https://github.com/allanmcarvalho/juriswany/releases/tag/" + tag}
        payload.update(changes or {})
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                requests.append((self.path, dict(self.headers)))
                if delay:
                    time.sleep(delay)
                self.send_response(status)
                if redirect:
                    self.send_header("Location", redirect)
                self.end_headers()
                try:
                    self.wfile.write(raw if raw is not None else json.dumps(payload).encode())
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def log_message(self, *_):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield "http://127.0.0.1:{}/latest".format(server.server_port), requests
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def updates(self, endpoint, force=True):
        args = ["atualizacoes", "--repositorio", str(self.repo), "--releases-url", endpoint]
        if force:
            args.append("--forcar")
        return self.cli(*args, package=self.codex)

    def marker(self):
        return self.codex / ".juriswany-install.json"

    def test_native_download_requires_real_git_objects_and_checks_inventory(self):
        commit = self.release_source()
        native = self.native_copy()
        first = self.stable(package=native, commit=commit)
        self.assertEqual(first["procedencia"]["commit"], commit)
        self.assertEqual(first["canal"], "stable")
        self.assertEqual(json.loads(self.marker().read_text())["formato"], 3)
        before = self.marker().read_bytes()
        (native / "SKILL.md").write_text("Conteúdo adulterado.\n", encoding="utf-8")
        self.stable(package=native, commit=commit, success=False)
        self.assertEqual(self.marker().read_bytes(), before)
        (native / "SKILL.md").write_bytes((self.package / "SKILL.md").read_bytes())
        for flag in ("extra.txt", "vazia", ".DS_Store", "local.pyc", "__pycache__"):
            extra = native / flag
            if flag in ("extra.txt", ".DS_Store", "local.pyc"):
                extra.write_text("Extra", encoding="utf-8")
            else:
                extra.mkdir()
            self.stable(package=native, commit=commit, success=False)
            if extra.is_dir():
                extra.rmdir()
            else:
                extra.unlink()
        (native / "SKILL.md").chmod(0o755)
        self.stable(package=native, commit=commit, success=False)
        (native / "SKILL.md").chmod(0o644)
        self.stable(package=native, commit="0" * 40, success=False)
        (self.repo / "README.md").write_text("Outro commit.\n", encoding="utf-8")
        later = self.commit()
        self.stable(package=native, commit=later, success=False)
        self.assertEqual(self.marker().read_bytes(), before)

    def test_external_origin_supports_bare_git_repository(self):
        commit = self.release_source()
        native = self.native_copy()
        bare = self.base / "objetos.git"
        self.git("clone", "--bare", str(self.repo), str(bare))
        result = self.install("--canal", "stable", "--release", "v0.2.0", "--origem-git",
                              str(bare), "--commit", commit, package=native)
        self.assertEqual(result["procedencia"]["commit"], commit)

    def test_external_executable_requires_owner_execute_permission(self):
        (self.package / "SKILL.md").chmod(0o755)
        commit = self.release_source()
        native = self.native_copy()
        (native / "SKILL.md").chmod(0o655)
        self.stable(package=native, commit=commit, success=False)
        self.assertFalse(self.codex.exists())

    def test_git_replacements_cannot_change_the_pinned_package(self):
        original = self.release_source()
        native = self.native_copy()
        (self.package / "SKILL.md").write_text("Outro pacote fictício.\n", encoding="utf-8")
        replaced = self.commit()
        self.git("replace", original, replaced)
        self.environment["GIT_NO_REPLACE_OBJECTS"] = "0"
        self.stable(commit=original, success=False)
        self.assertFalse(self.codex.exists())
        result = self.stable(package=native, commit=original)
        self.assertEqual(result["procedencia"]["commit"], original)
        self.assertEqual((self.codex / "SKILL.md").read_bytes(), (native / "SKILL.md").read_bytes())

    def test_stable_tag_must_match_the_package_version(self):
        self.release_source()
        self.git("tag", "v9.9.9")
        self.install("--canal", "stable", "--release", "v9.9.9", success=False)
        self.assertFalse(self.codex.exists())
        self.stable()
        before = self.marker().read_bytes()
        self.install("--canal", "stable", "--release", "v9.9.9", success=False)
        self.assertEqual(self.marker().read_bytes(), before)

    def test_origin_flags_and_stable_release_are_required_and_validated(self):
        self.release_source()
        for flags in (("--commit", "0" * 40), ("--origem-git", str(self.repo)),
                      ("--canal", "stable"), ("--canal", "dev", "--release", "v0.2.0"),
                      ("--canal", "stable", "--release", "v0.2.0-rc.1")):
            with self.subTest(flags=flags):
                self.install(*flags, success=False)
                self.assertFalse(self.codex.exists())

    def test_native_adoption_is_opt_in_exact_and_preserves_profile_and_files(self):
        commit = self.release_source()
        native = self.native_copy()
        shutil.copytree(native, self.codex)
        self.cli("perfil", "definir", "--nome", "Pessoa fictícia")
        profile = self.profile_file().read_bytes()
        before = {p.relative_to(self.codex): (p.read_bytes(), p.stat().st_mtime_ns)
                  for p in self.codex.rglob("*") if p.is_file()}
        self.stable(package=native, commit=commit, success=False)
        self.assertFalse(self.marker().exists())
        result = self.stable("--adotar-nativa", package=native, commit=commit)
        self.assertEqual(result["estado"], "adotado")
        self.assertEqual({p.relative_to(self.codex): (p.read_bytes(), p.stat().st_mtime_ns)
                          for p in self.codex.rglob("*") if p.is_file() and p != self.marker()}, before)
        self.assertEqual(self.profile_file().read_bytes(), profile)
        self.assertEqual(self.stable("--adotar-nativa", package=native, commit=commit)["estado"],
                         "ja_instalado")

    def test_native_adoption_rejects_modified_extra_directory_and_symlink(self):
        commit = self.release_source()
        native = self.native_copy()
        for issue in ("changed", "extra", "directory", "symlink", "marker-symlink"):
            with self.subTest(issue=issue):
                shutil.copytree(native, self.codex)
                if issue == "changed":
                    (self.codex / "SKILL.md").write_text("Anotação pessoal.", encoding="utf-8")
                elif issue == "extra":
                    (self.codex / "pessoal.txt").write_text("Preservar.", encoding="utf-8")
                elif issue == "directory":
                    (self.codex / "anotacoes").mkdir()
                elif issue == "marker-symlink":
                    self.marker().symlink_to(self.base / "marcador-ausente")
                else:
                    (self.codex / "SKILL.md").unlink()
                    (self.codex / "SKILL.md").symlink_to(native / "SKILL.md")
                self.stable("--adotar-nativa", package=native, commit=commit, success=False)
                self.assertFalse(self.marker().exists())
                self.assertEqual((native / "SKILL.md").read_bytes(), (self.package / "SKILL.md").read_bytes())
                shutil.rmtree(self.codex)

    def test_channels_preserve_existing_selection_and_only_rewrite_marker(self):
        self.release_source()
        self.assertEqual(self.install()["canal"], "dev")
        before = {p.relative_to(self.codex): (p.read_bytes(), p.stat().st_mtime_ns)
                  for p in self.codex.rglob("*") if p.is_file() and p != self.marker()}
        self.assertEqual(self.stable()["canal"], "stable")
        marker = self.marker().read_bytes(), self.marker().stat().st_mtime_ns
        self.assertEqual(self.install()["canal"], "stable")
        self.assertEqual((self.marker().read_bytes(), self.marker().stat().st_mtime_ns), marker)
        self.assertEqual(self.install("--canal", "dev")["release"], None)
        self.assertEqual({p.relative_to(self.codex): (p.read_bytes(), p.stat().st_mtime_ns)
                          for p in self.codex.rglob("*") if p.is_file() and p != self.marker()}, before)

    def test_native_adoption_preserves_changed_executable_mode(self):
        commit = self.release_source()
        native = self.native_copy()
        shutil.copytree(native, self.codex)
        script = self.codex / "scripts/local.py"
        script.chmod(0o755)
        self.stable("--adotar-nativa", package=native, commit=commit, success=False)
        self.assertFalse(self.marker().exists())
        self.assertEqual(script.stat().st_mode & 0o777, 0o755)

    def test_explicit_channel_change_records_selected_commit_with_same_package(self):
        origin = self.release_source()
        self.stable()
        (self.repo / "README.md").write_text("Mudança só na apresentação.\n", encoding="utf-8")
        head = self.commit()
        self.assertNotEqual(head, origin)
        result = self.install("--canal", "dev", "--origem-git", str(self.repo), "--commit", head)
        self.assertEqual(result["canal"], "dev")
        self.assertEqual(result["procedencia"]["commit"], head)
        self.assertEqual(json.loads(self.marker().read_text())["procedencia"]["commit"], head)

    def test_schema_one_is_strict_legacy_dev_and_migrates_idempotently(self):
        self.release_source()
        self.install()
        legacy = json.loads(self.marker().read_text())
        legacy.pop("canal")
        legacy.pop("release")
        legacy.pop("executaveis")
        legacy["formato"] = 1
        self.marker().write_text(json.dumps(legacy), encoding="utf-8")
        self.assertEqual(self.install()["canal"], "dev")
        self.assertEqual(json.loads(self.marker().read_text())["formato"], 3)
        before = self.marker().read_bytes(), self.marker().stat().st_mtime_ns
        self.install()
        self.assertEqual((self.marker().read_bytes(), self.marker().stat().st_mtime_ns), before)
        legacy["canal"] = "stable"
        self.marker().write_text(json.dumps(legacy), encoding="utf-8")
        self.install(success=False)
        self.assertEqual(json.loads(self.marker().read_text()), legacy)

    def test_stable_ignores_main_then_reports_release_without_installing(self):
        origin = self.release_source()
        self.stable()
        before = self.marker().read_bytes()
        self.publish()
        self.environment["GH_TOKEN"] = "token-ficticio-nao-enviar"
        self.environment["GITHUB_TOKEN"] = "outro-token-ficticio-nao-enviar"
        with self.api() as (endpoint, requests):
            current = self.updates(endpoint)
            self.assertEqual(current["estado"], "atual")
            self.assertEqual(current["commit_remoto"], origin)
            self.assertEqual(current["release_instalada"], "v0.2.0")
            self.assertNotIn("Authorization", requests[0][1])
        with self.api("v0.3.0") as (endpoint, _):
            newer = self.updates(endpoint)
            self.assertEqual(newer["estado"], "diferente")
            self.assertEqual(newer["release_publicada"], "v0.3.0")
        self.assertEqual(self.marker().read_bytes(), before)
        self.install("--canal", "dev")
        with self.api(status=500) as (endpoint, requests):
            self.assertEqual(self.updates(endpoint)["estado"], "atual")
            self.assertEqual(requests, [])

    def test_latest_404_is_sem_release_and_never_falls_back_to_main(self):
        self.release_source()
        self.stable()
        self.publish()
        with self.api(status=404) as (endpoint, _):
            result = self.updates(endpoint)
            self.assertEqual(result["estado"], "sem_release")
            self.assertNotIn("commit_remoto", result)
            self.assertEqual(result["canal"], "stable")

    def test_inconsistent_publication_is_not_presented_as_an_update(self):
        self.release_source()
        self.stable()
        before = self.marker().read_bytes()
        self.git("tag", "v0.3.0")
        with self.api("v0.3.0") as (endpoint, _):
            result = self.updates(endpoint)
        self.assertEqual(result["estado"], "indisponivel")
        self.assertEqual(result["release_publicada"], "v0.3.0")
        self.assertIn("manifesto", result["mensagem"])
        self.assertNotIn("conteudo_alterado", result)
        self.assertEqual(self.marker().read_bytes(), before)

    def test_api_invalid_responses_and_offline_are_informative(self):
        self.release_source()
        self.stable()
        for changes in ({"draft": True}, {"prerelease": True}, {"tag_name": "main"},
                        {"tag_name": "v0.3.0-rc.1"}, {"published_at": None},
                        {"published_at": "inválida"}, {"html_url": "https://example.invalid/"}):
            with self.subTest(changes=changes), self.api(changes=changes) as (endpoint, _):
                self.assertEqual(self.updates(endpoint)["estado"], "indisponivel")
        for raw in (b"{", b"[]", b"null", b"\\xff"):
            with self.subTest(raw=raw), self.api(raw=raw) as (endpoint, _):
                self.assertEqual(self.updates(endpoint)["estado"], "indisponivel")
        with self.api(status=500) as (endpoint, _):
            self.assertEqual(self.updates(endpoint)["estado"], "indisponivel")
        self.assertEqual(self.updates(endpoint)["estado"], "indisponivel")

    def test_http_timeout_and_redirects_do_not_escape_or_raise_tracebacks(self):
        self.release_source()
        self.stable()
        with self.api(delay=6) as (endpoint, _):
            self.assertEqual(self.updates(endpoint)["estado"], "indisponivel")
        with self.api() as (target, requests):
            with self.api(status=302, redirect=target) as (endpoint, _):
                self.assertEqual(self.updates(endpoint)["estado"], "indisponivel")
            self.assertEqual(requests, [])

    def test_external_origin_rejects_unbundled_license_and_symlink_git_tree(self):
        commit = self.initialize_git()
        shutil.copyfile(self.repo / "LICENSE", self.package / "LICENSE")
        native = self.native_copy()
        self.stable(package=native, commit=commit, success=False)
        (self.package / "LICENSE").unlink()
        (self.package / "LICENSE").symlink_to("../../LICENSE")
        linked = self.commit()
        self.install("--origem-git", str(self.repo), "--commit", linked, package=native,
                     success=False)
        self.assertFalse(self.codex.exists())
        (self.package / "LICENSE").unlink()
        (self.package / "LICENSE").write_bytes((self.repo / "LICENSE").read_bytes())
        (self.repo / "LICENSE").unlink()
        (self.repo / "LICENSE").symlink_to("skills/juriswany/LICENSE")
        root_link = self.commit()
        self.install("--origem-git", str(self.repo), "--commit", root_link, package=native,
                     success=False)
        self.assertFalse(self.codex.exists())

    def test_override_rejects_non_loopback_and_credentials_without_network(self):
        self.release_source()
        self.stable()
        for endpoint in ("https://example.invalid/latest", "http://example.invalid:80/latest",
                         "http://user:secret@127.0.0.1:80/latest", "file:///tmp/latest",
                         "http://127.0.0.1:80/latest?token=secret"):
            self.cli("atualizacoes", "--forcar", "--releases-url", endpoint,
                     package=self.codex, success=False)

    def test_cache_identity_includes_release_channel_and_endpoint(self):
        self.release_source()
        self.stable()
        with self.api() as (first, _):
            self.assertFalse(self.updates(first, force=False)["cache"])
            self.assertTrue(self.updates(first, force=False)["cache"])
            with self.api(status=404) as (second, _):
                self.assertFalse(self.updates(second, force=False)["cache"])
                self.assertEqual(self.updates(second, force=False)["estado"], "sem_release")
            self.install("--canal", "dev")
            self.assertFalse(self.updates(first, force=False)["cache"])


if __name__ == "__main__":
    unittest.main()
