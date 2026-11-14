#!/usr/bin/env python3
"""Instalação, preferências privadas e consulta consultiva do Juriswany."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
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


PACKAGE = Path(__file__).resolve().parent.parent
MARKER = ".juriswany-install.json"
OFFICIAL = "https://github.com/allanmcarvalho/juriswany.git"
DEFAULT_PROFILE = {
    "formato": 1, "revisao": 0, "resposta": "curta",
    "execucao": "economica", "consulta": "semanal",
}
OPTIONS = {
    "resposta": ("curta", "detalhada"),
    "execucao": ("economica", "equilibrada", "aprofundada"),
    "consulta": ("manual", "diaria", "semanal"),
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


def profile_path():
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "juriswany" / "perfil.json"


def validate_profile(value):
    fields = set(DEFAULT_PROFILE) | {"nome", "tratamento"}
    if (not isinstance(value, dict) or set(value) - fields
            or not set(DEFAULT_PROFILE).issubset(value)
            or type(value.get("formato")) is not int or value["formato"] != 1
            or type(value.get("revisao")) is not int or value["revisao"] < 0):
        raise LocalError("Perfil inválido ou versão desconhecida. O arquivo foi preservado.")
    for field, choices in OPTIONS.items():
        if value[field] not in choices:
            raise LocalError("Valor inválido para {} no perfil.".format(field))
    for field, limit in (("nome", 120), ("tratamento", 40)):
        if field in value:
            text = value[field]
            if (not isinstance(text, str) or not text.strip() or len(text) > limit
                    or any(ord(char) < 32 or ord(char) == 127 for char in text)):
                raise LocalError("{} deve ser texto de 1 a {} caracteres, sem controles.".format(field, limit))
    return value


def load_profile():
    path = profile_path()
    if path.parent.is_symlink():
        raise LocalError("Diretório do perfil não pode ser link simbólico.")
    if path.exists() or path.is_symlink():
        return validate_profile(read_json(path))
    return DEFAULT_PROFILE.copy()


def profile_command(args):
    if args.acao == "definir":
        changes = {key: getattr(args, key) for key in ("nome", "tratamento", *OPTIONS)
                   if getattr(args, key) is not None}
        if not changes:
            raise LocalError("Informe ao menos uma preferência para definir.")
        path = profile_path()
        private_dir(path.parent)
        with locked(path.parent / ".perfil.lock"):
            value = load_profile()
            value.update(changes)
            value["revisao"] += 1
            validate_profile(value)
            atomic_json(path, value)
        return {"estado": "salvo", "caminho": str(path), "perfil": value}
    value = load_profile()
    if args.acao == "exportar":
        lines = ["Preferências para esta conversa:"]
        if "nome" in value:
            lines.append("Meu nome é {}.".format(value["nome"]))
        if "tratamento" in value:
            lines.append("Use o tratamento {}.".format(value["tratamento"]))
        else:
            lines.append("Use tratamento neutro.")
        lines.extend([
            "Prefiro resposta {} e execução {}.".format(value["resposta"], value["execucao"]),
            "A preferência de consulta de atualizações é {}.".format(value["consulta"]),
            "Este bloco não garante memória em conversas futuras.",
        ])
        return {"estado": "exportado", "texto": "\n".join(lines)}
    return {"estado": "lido", "caminho": str(profile_path()), "perfil": value}


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


def manifest(root):
    value = read_json(root / "manifest.json")
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
    if (not isinstance(value, dict) or set(value) != {"gerenciador", "formato", "procedencia", "arquivos"}
            or value["gerenciador"] != "juriswany"
            or type(value["formato"]) is not int or value["formato"] != 1
            or not isinstance(value["arquivos"], dict) or not value["arquivos"]):
        raise LocalError("Marcador inválido em {}. Destino preservado.".format(root))
    validate_provenance(value["procedencia"])
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
    manifest(root)
    return value


def git(*arguments, cwd=None):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "/usr/bin/false",
                "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
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


def source_provenance(root, files, license_path):
    try:
        repo = Path(os.fsdecode(git("rev-parse", "--show-toplevel", cwd=root)).strip()).resolve()
        if root.resolve() != repo / "skills" / "juriswany":
            return {"tipo": "sem_procedencia"}
        commit = git("rev-parse", "HEAD", cwd=repo).decode().strip()
        tree = git("rev-parse", "HEAD:skills/juriswany", cwd=repo).decode().strip()
        entries = git("ls-tree", "-rz", "HEAD:skills/juriswany", cwd=repo).split(b"\x00")
        tracked = {}
        for entry in filter(None, entries):
            metadata, raw_name = entry.split(b"\t", 1)
            mode, kind, digest = metadata.split()
            name = raw_name.decode("utf-8")
            safe_relative(name)
            if mode not in (b"100644", b"100755") or kind != b"blob":
                return {"tipo": "sem_procedencia"}
            content = (root / name).read_bytes()
            algorithm = hashlib.sha1 if len(digest) == 40 else hashlib.sha256
            blob = b"blob " + str(len(content)).encode() + b"\x00" + content
            if algorithm(blob).hexdigest() != digest.decode():
                return {"tipo": "sem_procedencia"}
            tracked[name] = files.get(name)
        if set(tracked) != set(files):
            return {"tipo": "sem_procedencia"}
        tracked_dirs = {str(parent) for name in tracked for parent in PurePosixPath(name).parents}
        for current, dirs, _ in os.walk(root):
            dirs[:] = [name for name in dirs if name not in IGNORED]
            for name in dirs:
                if (Path(current) / name).relative_to(root).as_posix() not in tracked_dirs:
                    return {"tipo": "sem_procedencia"}
        if git("show", "HEAD:LICENSE", cwd=repo) != license_path.read_bytes():
            return {"tipo": "sem_procedencia"}
        return {"tipo": "git", "commit": commit, "arvore": tree}
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


def install(args):
    _, files, provenance, license_path = source_package()
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
        if destination.exists() or destination.is_symlink():
            current = managed(destination)
        if current and current["arquivos"] == files:
            if (provenance["tipo"] == "git"
                    and current["procedencia"].get("arvore") != provenance["arvore"]):
                current["procedencia"] = provenance
                atomic_json(destination / MARKER, current)
            return {"estado": "ja_instalado", "destino": str(destination), "recuperado": recovered,
                    "procedencia": current["procedencia"]}
        staging = Path(tempfile.mkdtemp(prefix="." + destination.name + ".stage-",
                                       dir=str(destination.parent)))
        try:
            for name in files:
                target = staging / name
                target.parent.mkdir(parents=True, exist_ok=True)
                source = license_path if name == "LICENSE" else PACKAGE / name
                shutil.copyfile(source, target)
            marker = {"gerenciador": "juriswany", "formato": 1,
                      "procedencia": provenance, "arquivos": files}
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
            "recuperado": recovered, "procedencia": provenance,
            "backup": str(backup) if current else None}


def updates(args):
    metadata, files, provenance, _ = source_package()
    if provenance["tipo"] != "git":
        return {"estado": "sem_procedencia", "mensagem": "Esta cópia não tem revisão Git verificável."}
    profile = load_profile()
    if profile["consulta"] == "manual" and not args.forcar:
        return {"estado": "indisponivel", "motivo": "consulta_automatica_desabilitada",
                "mensagem": "Use --forcar para consultar agora."}
    repository = args.repositorio or metadata["repositorio"]
    if args.repositorio:
        remote_path = Path(repository).expanduser()
        if not remote_path.is_absolute():
            remote_path = remote_path.absolute()
        repository = str(remote_path)
    cache_base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "juriswany"
    private_dir(cache_base)
    identity = "\x00".join((str(PACKAGE), repository, provenance["commit"], provenance["arvore"],
                           files["LICENSE"]))
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
                        and result.get("estado") in ("atual", "diferente", "indisponivel")):
                    return dict(result, cache=True)
            except (LocalError, KeyError, TypeError):
                pass
        result = {"commit_origem": provenance["commit"], "arvore_origem": provenance["arvore"],
                  "licenca_origem": files["LICENSE"],
                  "consultado_em": datetime.now(timezone.utc).isoformat(), "cache": False}
        try:
            with tempfile.TemporaryDirectory(prefix="consulta-", dir=str(cache_base)) as temporary:
                git("init", "--bare", temporary)
                git("fetch", "--depth=1", "--no-tags", "--", repository,
                    metadata["referencia"], cwd=temporary)
                commit = git("rev-parse", "FETCH_HEAD", cwd=temporary).decode().strip()
                tree = git("rev-parse", "FETCH_HEAD:" + metadata["caminho"], cwd=temporary).decode().strip()
                remote_license = hashlib.sha256(git("show", "FETCH_HEAD:LICENSE", cwd=temporary)).hexdigest()
            different = tree != provenance["arvore"] or remote_license != files["LICENSE"]
            result.update({"estado": "diferente" if different else "atual",
                           "commit_remoto": commit, "arvore_remota": tree,
                           "licenca_remota": remote_license})
            if different:
                result["mensagem"] = "O pacote publicado tem conteúdo diferente. A consulta não instala código."
            if not args.repositorio:
                result["comparacao"] = OFFICIAL.removesuffix(".git") + "/compare/" + provenance["commit"] + "..." + commit
        except LocalError as error:
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
    profile = commands.add_parser("perfil", help="Consultar ou definir preferências privadas.")
    actions = profile.add_subparsers(dest="acao", required=True)
    actions.add_parser("mostrar")
    actions.add_parser("exportar")
    setter = actions.add_parser("definir")
    setter.add_argument("--nome")
    setter.add_argument("--tratamento")
    for field, choices in OPTIONS.items():
        setter.add_argument("--" + field, choices=choices)
    update = commands.add_parser("atualizacoes", help="Comparar o pacote sem instalar código remoto.")
    update.add_argument("--forcar", action="store_true")
    update.add_argument("--repositorio")
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
