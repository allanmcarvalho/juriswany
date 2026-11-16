#!/usr/bin/env python3
"""Instalação, preferências privadas e consulta consultiva do Juriswany."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
from http.client import HTTPException
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, ProxyHandler, build_opener


PACKAGE = Path(__file__).resolve().parent.parent
MARKER = ".juriswany-install.json"
OFFICIAL = "https://github.com/allanmcarvalho/juriswany.git"
RELEASES = "https://api.github.com/repos/allanmcarvalho/juriswany/releases/latest"
RELEASE_TAG = r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
PREFERENCES = {
    "nome": {"limite": 120},
    "tratamento": {"limite": 40},
    "resposta": {"padrao": "curta", "opcoes": ("curta", "detalhada")},
    "execucao": {"padrao": "economica", "opcoes": ("economica", "equilibrada", "aprofundada")},
    "consulta": {"padrao": "semanal", "opcoes": ("manual", "diaria", "semanal")},
}
IGNORED = {"__pycache__", ".DS_Store", ".git", ".pytest_cache"}


class LocalError(Exception):
    pass


def read_json(path):
    if path.is_symlink():
        raise LocalError("Link simbólico não permitido em {}.".format(path))
    if not path.is_file():
        raise LocalError("JSON deve ser um arquivo regular em {}.".format(path))
    try:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)
    except (ValueError, UnicodeError) as error:
        raise LocalError("JSON inválido em {}. O arquivo foi preservado.".format(path)) from error


def private_dir(path):
    if path.is_symlink():
        raise LocalError("Diretório privado não pode ser link simbólico: {}.".format(path))
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)


@contextmanager
def locked(path):
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(path), flags, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise LocalError("Bloqueio não é arquivo regular: {}.".format(path))
        os.fchmod(fd, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def atomic_json(path, value):
    fd, name = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def xdg_path(variable, fallback):
    configured = os.environ.get(variable)
    if configured and Path(configured).is_absolute():
        return Path(configured)
    return Path.home() / fallback


def profile_path():
    return xdg_path("XDG_CONFIG_HOME", ".config") / "juriswany" / "perfil.json"


def default_profile():
    return {"formato": 2, "revisao": 0, "decisoes": {},
            **{field: spec["padrao"] for field, spec in PREFERENCES.items() if "padrao" in spec}}


def validate_profile(value):
    required = {"formato", "revisao"}
    fields = set(PREFERENCES) | required | {"decisoes"}
    if (not isinstance(value, dict) or set(value) - fields or not required.issubset(value)
            or type(value.get("formato")) is not int or value["formato"] not in (1, 2)
            or type(value.get("revisao")) is not int or value["revisao"] < 0):
        raise LocalError("Perfil inválido ou versão desconhecida. O arquivo foi preservado.")
    for field, spec in PREFERENCES.items():
        if field in value:
            text = value[field]
            if "opcoes" in spec:
                if text not in spec["opcoes"]:
                    raise LocalError("Valor inválido para {} no perfil.".format(field))
            elif (not isinstance(text, str) or not text.strip() or len(text) > spec["limite"]
                  or any(ord(char) < 32 or ord(char) == 127 for char in text)):
                raise LocalError("{} deve ser texto de 1 a {} caracteres, sem controles.".format(field, spec["limite"]))
    normalized = dict(value)
    if value["formato"] == 1:
        if "decisoes" in value or not {"resposta", "execucao", "consulta"}.issubset(value):
            raise LocalError("Perfil legado inválido ou incompleto. O arquivo foi preservado.")
        normalized.update(formato=2, decisoes={
            field: "configurada" for field, spec in PREFERENCES.items()
            if field in value and ("padrao" not in spec or value[field] != spec["padrao"])})
    decisions = normalized.get("decisoes")
    if (not isinstance(decisions, dict) or set(decisions) - set(PREFERENCES)
            or any(state not in ("configurada", "ignorada") for state in decisions.values())):
        raise LocalError("Decisões inválidas no perfil. O arquivo foi preservado.")
    for field, spec in PREFERENCES.items():
        if decisions.get(field) == "configurada":
            consistent = field in normalized
        elif "padrao" in spec:
            consistent = normalized.get(field, spec["padrao"]) == spec["padrao"]
            normalized.setdefault(field, spec["padrao"])
        else:
            consistent = field not in normalized
        if not consistent:
            raise LocalError("Valor e decisão incompatíveis para {}. O arquivo foi preservado.".format(field))
    normalized["decisoes"] = dict(decisions)
    return normalized


def pending_preferences(profile):
    return [field for field in PREFERENCES if field not in profile["decisoes"]]


def apply_preferences(profile, changes, ignored):
    if not changes and not ignored:
        raise LocalError("Informe ao menos uma preferência para definir ou ignorar.")
    if (set(changes) | set(ignored)) - set(PREFERENCES):
        raise LocalError("Preferência desconhecida.")
    if set(changes) & set(ignored):
        raise LocalError("Não é possível definir e ignorar a mesma preferência no mesmo pedido.")
    value = dict(profile, decisoes=dict(profile["decisoes"]))
    for field in ignored:
        if "padrao" in PREFERENCES[field]:
            value[field] = PREFERENCES[field]["padrao"]
        else:
            value.pop(field, None)
        value["decisoes"][field] = "ignorada"
    value.update(changes)
    value["decisoes"].update({field: "configurada" for field in changes})
    value["revisao"] += 1
    return validate_profile(value)


def load_profile():
    path = profile_path()
    if path.parent.is_symlink():
        raise LocalError("Diretório do perfil não pode ser link simbólico.")
    if path.exists() or path.is_symlink():
        return validate_profile(read_json(path))
    return default_profile()


def profile_command(args):
    if args.acao == "definir":
        changes = {key: getattr(args, key) for key in PREFERENCES
                   if getattr(args, key) is not None}
        apply_preferences(default_profile(), changes, args.ignorar)
        path = profile_path()
        private_dir(path.parent)
        with locked(path.parent / ".perfil.lock"):
            value = apply_preferences(load_profile(), changes, args.ignorar)
            atomic_json(path, value)
        return {"estado": "salvo", "caminho": str(path), "perfil": value,
                "pendentes": pending_preferences(value)}
    value = load_profile()
    if args.acao == "exportar":
        lines = ["Preferências para esta conversa:"]
        address = " ".join(value[field] for field in ("tratamento", "nome") if field in value)
        if address:
            lines.append("Chame-me de {} nas respostas dirigidas a mim.".format(address))
        for field in PREFERENCES:
            state = value["decisoes"].get(field)
            if state == "configurada":
                lines.append("Confirmada: {} = {}.".format(field, value[field]))
            elif state == "ignorada":
                lines.append("Não ofereça configurar {}. Esta opção foi recusada expressamente.".format(field))
                if field in value:
                    lines.append("Padrão efetivo de {} = {}.".format(field, value[field]))
            else:
                detail = " Padrão efetivo = {}.".format(value[field]) if field in value else ""
                lines.append("Pendente: {}. Ainda não houve escolha nem recusa.{}".format(field, detail))
        lines.extend(["Ofereça configurar somente os campos pendentes uma vez por conversa, sem bloquear a tarefa.",
                      "Use nome e tratamento confirmados nas respostas seguintes, sem inseri-los automaticamente em documentos de terceiros.",
                      "Este bloco não garante memória em conversas futuras."])
        return {"estado": "exportado", "texto": "\n".join(lines), "pendentes": pending_preferences(value)}
    return {"estado": "lido", "caminho": str(profile_path()), "perfil": value,
            "pendentes": pending_preferences(value)}


def safe_relative(name):
    if (not isinstance(name, str) or not name or "\\" in name or "\x00" in name
            or PurePosixPath(name).is_absolute() or name != PurePosixPath(name).as_posix()
            or any(part in (".", "..") for part in name.split("/"))):
        raise LocalError("Caminho inválido no marcador ou pacote.")
    return name


def snapshot(root, source=False):
    if root.is_symlink() or not root.is_dir():
        raise LocalError("A pasta não é um diretório regular: {}.".format(root))
    files = {}
    for current, dirs, names in os.walk(root, followlinks=False):
        for name in list(dirs):
            child = Path(current) / name
            if source and name in IGNORED:
                dirs.remove(name)
            elif child.is_symlink():
                raise LocalError("Link simbólico não permitido no pacote: {}.".format(child))
        for name in names:
            child = Path(current) / name
            relative = child.relative_to(root).as_posix()
            if relative == MARKER or (source and (name in IGNORED or name.endswith(".pyc"))):
                continue
            safe_relative(relative)
            if child.is_symlink() or not child.is_file():
                raise LocalError("Arquivo irregular no pacote: {}.".format(child))
            files[relative] = hashlib.sha256(child.read_bytes()).hexdigest()
    return files


def validate_manifest(value):
    expected = {"formato", "nome", "versao", "repositorio", "referencia", "caminho"}
    if (not isinstance(value, dict) or set(value) != expected
            or type(value["formato"]) is not int or value["formato"] != 1
            or value["nome"] != "juriswany" or value["repositorio"] != OFFICIAL
            or value["referencia"] != "refs/heads/main"
            or value["caminho"] != "skills/juriswany"
            or not isinstance(value["versao"], str)
            or not re.fullmatch(r"\d+\.\d+\.\d+", value["versao"])):
        raise LocalError("Manifesto inválido ou incompatível.")
    return value


def manifest(root):
    return validate_manifest(read_json(root / "manifest.json"))


def executable_files(root, files):
    return sorted(name for name in files
                  if (name != "LICENSE" or (root / name).exists())
                  and (root / name).stat().st_mode & stat.S_IXUSR)


def validate_provenance(value):
    if value == {"tipo": "sem_procedencia"}:
        return value
    if (not isinstance(value, dict) or set(value) != {"tipo", "commit", "arvore"}
            or value["tipo"] != "git"
            or not all(isinstance(value[key], str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value[key])
                       for key in ("commit", "arvore"))):
        raise LocalError("Procedência inválida no marcador.")
    return value


def managed(root):
    if root.is_symlink() or not root.is_dir():
        raise LocalError("Instalação desconhecida ou link simbólico em {}. Destino preservado.".format(root))
    marker = root / MARKER
    if not marker.is_file() or marker.is_symlink():
        raise LocalError("Instalação desconhecida em {}. Destino preservado.".format(root))
    value = read_json(marker)
    common = {"gerenciador", "formato", "procedencia", "arquivos"}
    if (not isinstance(value, dict) or type(value.get("formato")) is not int
            or value["formato"] not in (1, 2, 3)
            or set(value) != (common if value["formato"] == 1 else
                              common | {"canal", "release"} |
                              ({"executaveis"} if value["formato"] == 3 else set()))
            or value["gerenciador"] != "juriswany"
            or not isinstance(value["arquivos"], dict) or not value["arquivos"]):
        raise LocalError("Marcador inválido em {}. Destino preservado.".format(root))
    validate_provenance(value["procedencia"])
    if value["formato"] == 1:
        value = dict(value, canal="dev", release=None)
    elif (value["canal"] not in ("stable", "dev")
          or (value["canal"] == "dev" and value["release"] is not None)
          or (value["canal"] == "stable" and
              (value["procedencia"]["tipo"] != "git" or not valid_tag(value["release"])))):
        raise LocalError("Canal ou release inválida no marcador. Destino preservado.")
    for name, digest in value["arquivos"].items():
        safe_relative(name)
        if name == MARKER or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise LocalError("Mapa de arquivos inválido. Destino preservado.")
    if not {"manifest.json", "SKILL.md", "scripts/local.py", "LICENSE"}.issubset(value["arquivos"]):
        raise LocalError("Marcador não descreve um pacote completo. Destino preservado.")
    present = snapshot(root)
    expected = value["arquivos"]
    allowed_dirs = {str(parent) for name in expected for parent in PurePosixPath(name).parents
                    if str(parent) != "."}
    extra_dirs = {path.relative_to(root).as_posix() for path in root.rglob("*")
                  if path.is_dir()} - allowed_dirs
    if present != expected or extra_dirs:
        raise LocalError("Instalação contém alterações ou arquivos extras em {}. Destino preservado.".format(root))
    if value["formato"] == 3:
        modes = value["executaveis"]
        if (not isinstance(modes, list) or not all(isinstance(name, str) for name in modes)
                or modes != sorted(set(modes)) or not set(modes).issubset(expected)
                or modes != executable_files(root, expected)):
            raise LocalError("Modos executáveis alterados ou inválidos. Destino preservado.")
    metadata = manifest(root)
    if value["canal"] == "stable" and value["release"] != "v" + metadata["versao"]:
        raise LocalError("A release não corresponde à versão do manifesto. Destino preservado.")
    return value


def git(*arguments, cwd=None):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "/usr/bin/false",
                "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                "GIT_NO_REPLACE_OBJECTS": "1",
                "GIT_SSH_COMMAND": "ssh -oBatchMode=yes -oConnectTimeout=5"})
    try:
        result = subprocess.run(
            ["git", "-c", "protocol.ext.allow=never", "-c", "core.hooksPath=" + os.devnull,
             *arguments], cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=20, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise LocalError("Git indisponível ou consulta excedeu o tempo limite.") from error
    if result.returncode:
        raise LocalError("Git não conseguiu consultar a revisão solicitada.")
    return result.stdout


def valid_tag(value):
    return isinstance(value, str) and re.fullmatch(RELEASE_TAG, value) is not None


def git_license(repo, revision):
    entry = git("ls-tree", "-z", revision, "--", "LICENSE", cwd=repo)
    if not re.fullmatch(rb"(100644|100755) blob ([0-9a-f]{40}|[0-9a-f]{64})\tLICENSE\x00", entry):
        raise LocalError("LICENSE deve ser um arquivo regular na árvore Git da origem.")
    return git("show", revision + ":LICENSE", cwd=repo)


def verified_provenance(root, files, license_path, repo, commit, external=False):
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit):
        raise LocalError("Informe o SHA completo do commit da origem.")
    resolved = git("rev-parse", "--verify", commit + "^{commit}", cwd=repo).decode().strip()
    if resolved != commit:
        raise LocalError("O SHA não identifica o commit fornecido.")
    tree = git("rev-parse", commit + ":skills/juriswany", cwd=repo).decode().strip()
    entries = git("ls-tree", "-rz", commit + ":skills/juriswany", cwd=repo).split(b"\x00")
    tracked = set()
    for entry in filter(None, entries):
        metadata, raw_name = entry.split(b"\t", 1)
        mode, kind, digest = metadata.split()
        name = raw_name.decode("utf-8")
        safe_relative(name)
        if mode not in (b"100644", b"100755") or kind != b"blob":
            raise LocalError("A árvore Git contém tipo ou modo não permitido.")
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise LocalError("Arquivo da origem ausente ou irregular.")
        if bool(path.stat().st_mode & stat.S_IXUSR) != (mode == b"100755"):
            raise LocalError("Modo do arquivo diverge da árvore Git.")
        content = path.read_bytes()
        if git("cat-file", "blob", digest.decode(), cwd=repo) != content:
            raise LocalError("O conteúdo do pacote diverge do commit fornecido.")
        tracked.add(name)
    expected = set(files)
    if "LICENSE" not in tracked:
        if external:
            raise LocalError("A árvore da origem externa não contém LICENSE no pacote.")
        expected.discard("LICENSE")
    if tracked != expected:
        raise LocalError("O inventário do pacote diverge da árvore Git.")
    tracked_dirs = {str(parent) for name in tracked for parent in PurePosixPath(name).parents}
    for current, dirs, _ in os.walk(root):
        if not external:
            dirs[:] = [name for name in dirs if name not in IGNORED]
        for name in dirs:
            if (Path(current) / name).relative_to(root).as_posix() not in tracked_dirs:
                raise LocalError("O pacote contém diretório extra.")
    if git_license(repo, commit) != license_path.read_bytes():
        raise LocalError("A licença do pacote diverge da licença da origem.")
    return {"tipo": "git", "commit": commit, "arvore": tree}


def local_repository(root):
    repo = Path(os.fsdecode(git("rev-parse", "--show-toplevel", cwd=root)).strip()).resolve()
    if root.resolve() != repo / "skills" / "juriswany":
        raise LocalError("O pacote não ocupa o caminho oficial na origem Git.")
    return repo


def source_provenance(root, files, license_path):
    try:
        repo = local_repository(root)
        commit = git("rev-parse", "HEAD", cwd=repo).decode().strip()
        return verified_provenance(root, files, license_path, repo, commit)
    except (LocalError, OSError, UnicodeError, ValueError):
        return {"tipo": "sem_procedencia"}


def source_package():
    metadata = manifest(PACKAGE)
    if (PACKAGE / MARKER).exists() or (PACKAGE / MARKER).is_symlink():
        installed = managed(PACKAGE)
        return metadata, installed["arquivos"], installed["procedencia"], PACKAGE / "LICENSE"
    files = snapshot(PACKAGE, source=True)
    if not {"SKILL.md", "scripts/local.py", "manifest.json"}.issubset(files):
        raise LocalError("Pacote incompleto.")
    license_path = PACKAGE / "LICENSE"
    if not license_path.exists():
        license_path = PACKAGE.parent.parent / "LICENSE"
    if license_path.is_symlink() or not license_path.is_file():
        raise LocalError("LICENSE não encontrada como arquivo regular junto ao pacote ou na raiz.")
    provenance = source_provenance(PACKAGE, files, license_path)
    files["LICENSE"] = hashlib.sha256(license_path.read_bytes()).hexdigest()
    return metadata, files, provenance, license_path


@contextmanager
def shortcut_links(destination, files):
    links = {}
    for name in sorted(files):
        parts = PurePosixPath(name).parts
        if len(parts) == 3 and parts[0] == "atalhos" and parts[2] == "SKILL.md":
            skill = parts[1]
            if not re.fullmatch(r"juriswany-[a-z0-9]+(?:-[a-z0-9]+)*", skill) or len(skill) > 64:
                raise LocalError("Nome de atalho inválido no pacote.")
            link = destination.parent / skill
            target = Path(destination.name) / "atalhos" / skill
            if link.is_symlink():
                if os.readlink(link) != str(target):
                    raise LocalError("Atalho desconhecido em {}. Destino preservado.".format(link))
            elif link.exists():
                raise LocalError("O caminho do atalho já está ocupado: {}. Destino preservado.".format(link))
            links[link] = target
    created = []
    try:
        for link, target in links.items():
            if link.is_symlink() and os.readlink(link) == str(target):
                continue
            link.symlink_to(target, target_is_directory=True)
            created.append(link)
        yield [str(link) for link in links]
    except BaseException:
        for link in reversed(created):
            if link.is_symlink() and os.readlink(link) == str(links[link]):
                link.unlink()
        raise


def install(args):
    metadata, files, provenance, license_path = source_package()
    executables = executable_files(PACKAGE, files)
    if (args.origem_git is None) != (args.commit is None):
        raise LocalError("Use --origem-git e --commit juntos.")
    if args.release and not valid_tag(args.release):
        raise LocalError("Release deve seguir vMAJOR.MINOR.PATCH, sem prerelease.")
    if args.origem_git is not None:
        origin = Path(args.origem_git).expanduser().resolve()
        if not (PACKAGE / "LICENSE").is_file():
            raise LocalError("A origem externa exige LICENSE dentro do pacote.")
        try:
            files = snapshot(PACKAGE)
            provenance = verified_provenance(PACKAGE, files, license_path, origin,
                                             args.commit, external=True)
        except (UnicodeError, ValueError) as error:
            raise LocalError("Objetos Git inválidos na origem fornecida.") from error
    else:
        origin = None
    if args.adotar_nativa and provenance["tipo"] != "git":
        raise LocalError("A adoção exige uma origem Git verificada.")
    if args.destino:
        requested = Path(args.destino).expanduser().absolute()
    else:
        host = ".agents" if args.host == "codex" else ".claude"
        requested = Path.home() / host / "skills" / "juriswany"
    if requested == Path(requested.anchor):
        raise LocalError("O destino deve ser uma pasta de skill.")
    requested.parent.mkdir(parents=True, exist_ok=True)
    destination = requested.parent.resolve() / requested.name
    backup = destination.with_name("." + destination.name + ".backup")
    recovered = False
    with locked(destination.with_name("." + destination.name + ".lock")):
        if backup.exists() or backup.is_symlink():
            managed(backup)
            if not destination.exists() and not destination.is_symlink():
                backup.rename(destination)
                recovered = True
        current = None
        adopt = False
        if destination.exists() or destination.is_symlink():
            if (args.adotar_nativa and not (destination / MARKER).exists()
                    and not (destination / MARKER).is_symlink()):
                if destination.is_symlink() or snapshot(destination) != files:
                    raise LocalError("A cópia nativa difere da origem verificada. Destino preservado.")
                if any(bool((destination / name).stat().st_mode & stat.S_IXUSR)
                       != bool((PACKAGE / name).stat().st_mode & stat.S_IXUSR) for name in files):
                    raise LocalError("O modo dos arquivos da cópia nativa foi alterado. Destino preservado.")
                allowed_dirs = {str(parent) for name in files for parent in PurePosixPath(name).parents}
                if any(path.relative_to(destination).as_posix() not in allowed_dirs
                       for path in destination.rglob("*") if path.is_dir()):
                    raise LocalError("A cópia nativa contém diretório extra. Destino preservado.")
                adopt = True
            else:
                current = managed(destination)
                if (current["formato"] < 3 and set(executable_files(destination, current["arquivos"]))
                        != set(executables).intersection(current["arquivos"])):
                    raise LocalError("O marcador antigo não comprova os modos anteriores. Destino preservado.")
        channel = args.canal or (current["canal"] if current else "dev")
        release = args.release
        if channel == "dev" and release is not None:
            raise LocalError("O canal dev não aceita --release.")
        if channel == "stable":
            if release is None and current and current["canal"] == "stable":
                release = current["release"]
            if not valid_tag(release) or provenance["tipo"] != "git":
                raise LocalError("O canal stable exige --release e procedência Git verificada.")
            if release != "v" + metadata["versao"]:
                raise LocalError("A release não corresponde à versão do manifesto.")
            if origin is None:
                try:
                    origin = local_repository(PACKAGE)
                except LocalError:
                    if not (current and current["canal"] == "stable"
                            and release == current["release"] and files == current["arquivos"]
                            and provenance == current["procedencia"]):
                        raise LocalError("Forneça os objetos Git para verificar a tag da release.")
            if origin is not None:
                tagged = git("rev-parse", "--verify", "refs/tags/" + release + "^{commit}",
                             cwd=origin).decode().strip()
                if tagged != provenance["commit"]:
                    raise LocalError("A tag da release não aponta para o commit verificado.")
        with shortcut_links(destination, files) as shortcuts:
            marker = {"gerenciador": "juriswany", "formato": 3, "procedencia": provenance,
                      "arquivos": files, "canal": channel, "release": release,
                      "executaveis": executables}
            if adopt:
                atomic_json(destination / MARKER, marker)
                return {"estado": "adotado", "destino": str(destination), "recuperado": recovered,
                        "procedencia": provenance, "canal": channel, "release": release,
                        "atalhos": shortcuts}
            if (current and current["arquivos"] == files
                    and executable_files(destination, files) == executables):
                refreshed = dict(current, formato=3, canal=channel, release=release, executaveis=executables)
                if (provenance["tipo"] == "git"
                        and (current["procedencia"].get("arvore") != provenance["arvore"]
                             or current["canal"] != channel
                             or (channel == "stable" and current.get("release") != release))):
                    refreshed["procedencia"] = provenance
                if refreshed != current:
                    atomic_json(destination / MARKER, refreshed)
                return {"estado": "ja_instalado", "destino": str(destination), "recuperado": recovered,
                        "procedencia": refreshed["procedencia"], "canal": channel, "release": release,
                        "atalhos": shortcuts}
            staging = Path(tempfile.mkdtemp(prefix="." + destination.name + ".stage-",
                                           dir=str(destination.parent)))
            try:
                for name in files:
                    target = staging / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source = license_path if name == "LICENSE" else PACKAGE / name
                    shutil.copyfile(source, target)
                    target.chmod(0o755 if name in executables else 0o644)
                atomic_json(staging / MARKER, marker)
                managed(staging)
                if current:
                    if backup.exists():
                        discarded = Path(tempfile.mkdtemp(prefix="." + destination.name + ".discard-",
                                                          dir=str(destination.parent)))
                        backup.rename(discarded)
                        shutil.rmtree(discarded)
                    destination.rename(backup)
                staging.rename(destination)
            except BaseException:
                if not destination.exists() and backup.exists():
                    backup.rename(destination)
                raise
            finally:
                if staging.exists():
                    shutil.rmtree(staging)
    return {"estado": "substituido" if current else "instalado", "destino": str(destination),
            "recuperado": recovered, "procedencia": provenance, "canal": channel, "release": release,
            "backup": str(backup) if current else None, "atalhos": shortcuts}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LocalError("Redirecionamento inesperado na API de releases.")


def releases_endpoint(override):
    if override is None:
        return RELEASES
    try:
        parsed = urlsplit(override)
        valid = (parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "::1", "localhost")
                 and parsed.port is not None and not parsed.username and not parsed.password
                 and not parsed.fragment and not parsed.query)
    except ValueError as error:
        raise LocalError("Endpoint de teste inválido.") from error
    if not valid:
        raise LocalError("--releases-url aceita somente HTTP em loopback com porta explícita.")
    return override


def latest_release(endpoint):
    request = Request(endpoint, headers={"Accept": "application/vnd.github+json",
                                         "User-Agent": "Juriswany"})
    try:
        opener = build_opener(NoRedirect, *([ProxyHandler({})] if endpoint != RELEASES else []))
        with opener.open(request, timeout=5) as response:
            if response.status != 200:
                raise LocalError("Resposta inesperada da API de releases.")
            payload = response.read(1048577)
            if len(payload) > 1048576:
                raise LocalError("Resposta da API de releases excedeu o limite.")
        value = json.loads(payload)
        if (not isinstance(value, dict) or value.get("draft") is not False
                or value.get("prerelease") is not False or not valid_tag(value.get("tag_name"))
                or not isinstance(value.get("published_at"), str)):
            raise LocalError("A API não retornou uma release estável publicada válida.")
        published = datetime.fromisoformat(value["published_at"].replace("Z", "+00:00"))
        if published.tzinfo is None:
            raise LocalError("Data de publicação inválida na release.")
        tag = value["tag_name"]
        link = OFFICIAL[:-4] + "/releases/tag/" + tag
        if value.get("html_url") != link:
            raise LocalError("A API retornou um link de release inesperado.")
        return tag
    except HTTPError as error:
        if error.code == 404:
            return None
        raise LocalError("API de releases indisponível (HTTP {}).".format(error.code)) from error
    except (URLError, TimeoutError, OSError, ValueError, UnicodeError, HTTPException, RecursionError) as error:
        raise LocalError("Não foi possível consultar uma release válida no tempo limite.") from error


def updates(args):
    metadata, files, provenance, _ = source_package()
    installed = managed(PACKAGE) if (PACKAGE / MARKER).exists() else None
    channel = installed["canal"] if installed else "dev"
    release = installed["release"] if installed else None
    endpoint = releases_endpoint(args.releases_url)
    if provenance["tipo"] != "git":
        return {"estado": "sem_procedencia", "canal": channel, "release_instalada": release,
                "mensagem": "Esta cópia não tem revisão Git verificável."}
    profile = load_profile()
    if profile["consulta"] == "manual" and not args.forcar:
        return {"estado": "indisponivel", "canal": channel, "release_instalada": release,
                "motivo": "consulta_automatica_desabilitada",
                "mensagem": "Use --forcar para consultar agora."}
    repository = args.repositorio or metadata["repositorio"]
    if args.repositorio:
        remote_path = Path(repository).expanduser()
        if not remote_path.is_absolute():
            remote_path = remote_path.absolute()
        repository = str(remote_path)
    cache_base = xdg_path("XDG_CACHE_HOME", ".cache") / "juriswany"
    private_dir(cache_base)
    identity = "\x00".join((str(PACKAGE), repository, provenance["commit"], provenance["arvore"],
                           files["LICENSE"], channel, release or "", endpoint))
    cache = cache_base / (hashlib.sha256(identity.encode()).hexdigest() + ".json")
    interval = {"diaria": 86400, "semanal": 604800, "manual": 0}[profile["consulta"]]
    with locked(cache.with_suffix(".lock")):
        if cache.exists() and not args.forcar:
            try:
                previous = read_json(cache)
                age = time.time() - previous["horario"]
                result = previous["resultado"]
                if (type(previous["horario"]) in (int, float) and 0 <= age < interval
                        and isinstance(result, dict)
                        and result.get("estado") in ("atual", "diferente", "indisponivel", "sem_release")):
                    return dict(result, cache=True)
            except (LocalError, KeyError, TypeError):
                pass
        result = {"canal": channel, "release_instalada": release,
                  "commit_origem": provenance["commit"], "arvore_origem": provenance["arvore"],
                  "licenca_origem": files["LICENSE"],
                  "consultado_em": datetime.now(timezone.utc).isoformat(), "cache": False}
        try:
            published = latest_release(endpoint) if channel == "stable" else None
            result["release_publicada"] = published
            if channel == "stable" and published is None:
                result.update({"estado": "sem_release", "mensagem": "Nenhuma release estável publicada."})
                atomic_json(cache, {"formato": 1, "horario": time.time(), "resultado": result})
                return result
            reference = "refs/tags/" + published if channel == "stable" else metadata["referencia"]
            with tempfile.TemporaryDirectory(prefix="consulta-", dir=str(cache_base)) as temporary:
                git("init", "--bare", temporary)
                git("fetch", "--depth=1", "--no-tags", "--", repository,
                    reference, cwd=temporary)
                commit = git("rev-parse", "FETCH_HEAD^{commit}", cwd=temporary).decode().strip()
                tree = git("rev-parse", "FETCH_HEAD:" + metadata["caminho"], cwd=temporary).decode().strip()
                if channel == "stable":
                    remote_manifest = validate_manifest(json.loads(git(
                        "show", "FETCH_HEAD:" + metadata["caminho"] + "/manifest.json", cwd=temporary)))
                    if "v" + remote_manifest["versao"] != published:
                        raise LocalError("A release publicada não corresponde à versão do manifesto.")
                remote_license = hashlib.sha256(git_license(temporary, "FETCH_HEAD")).hexdigest()
                listing = git("ls-tree", "FETCH_HEAD:" + metadata["caminho"], cwd=temporary)
                if any(entry.endswith(b"\tLICENSE") for entry in listing.splitlines()):
                    packaged_license = hashlib.sha256(git("show", "FETCH_HEAD:" + metadata["caminho"]
                                                          + "/LICENSE", cwd=temporary)).hexdigest()
                    if packaged_license != remote_license:
                        raise LocalError("As licenças da release e do pacote divergem.")
            content_changed = tree != provenance["arvore"] or remote_license != files["LICENSE"]
            release_changed = channel == "stable" and published != release
            result.update({"estado": "diferente" if content_changed or release_changed else "atual",
                           "conteudo_alterado": content_changed, "release_diferente": release_changed,
                           "commit_remoto": commit, "arvore_remota": tree,
                           "licenca_remota": remote_license})
            if content_changed:
                result["mensagem"] = "O pacote publicado tem conteúdo diferente. A consulta não instala código."
            if not args.repositorio:
                result["comparacao"] = OFFICIAL.removesuffix(".git") + "/compare/" + provenance["commit"] + "..." + commit
        except (LocalError, OSError, UnicodeError, ValueError) as error:
            result.update({"estado": "indisponivel", "mensagem": str(error)})
        atomic_json(cache, {"formato": 1, "horario": time.time(), "resultado": result})
        return result


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise LocalError("Argumentos inválidos. " + message)


def main():
    parser = Parser(description=__doc__)
    commands = parser.add_subparsers(dest="comando", required=True)
    installer = commands.add_parser("instalar", help="Instalar cópia revisável da skill.")
    installer.add_argument("host", choices=("codex", "claude"))
    installer.add_argument("--destino")
    installer.add_argument("--canal", choices=("stable", "dev"))
    installer.add_argument("--release")
    installer.add_argument("--origem-git")
    installer.add_argument("--commit")
    installer.add_argument("--adotar-nativa", action="store_true")
    profile = commands.add_parser("perfil", help="Consultar ou definir preferências privadas.")
    actions = profile.add_subparsers(dest="acao", required=True)
    actions.add_parser("mostrar")
    actions.add_parser("exportar")
    setter = actions.add_parser("definir")
    for field, spec in PREFERENCES.items():
        setter.add_argument("--" + field, choices=spec.get("opcoes"))
    setter.add_argument("--ignorar", action="append", choices=tuple(PREFERENCES), default=[])
    update = commands.add_parser("atualizacoes", help="Comparar o pacote sem instalar código remoto.")
    update.add_argument("--forcar", action="store_true")
    update.add_argument("--repositorio")
    update.add_argument("--releases-url")
    try:
        args = parser.parse_args()
        if args.comando == "instalar":
            result = install(args)
        elif args.comando == "perfil":
            result = profile_command(args)
        else:
            result = updates(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (LocalError, OSError) as error:
        print(json.dumps({"estado": "erro", "mensagem": str(error)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
