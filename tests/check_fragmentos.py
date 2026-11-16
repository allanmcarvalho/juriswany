from collections import Counter
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "docs" / "pesquisa"
INDEX = LIBRARY / "fragmentos.md"
CHAPTERS = sorted((LIBRARY / "fragmentos").glob("*.md"))
DOCUMENTS = [LIBRARY / "README.md", INDEX, *CHAPTERS]
texts = {path: path.read_text(encoding="utf-8") for path in DOCUMENTS}
errors = []
anchors = {}
identifiers = {}
link_count = 0

if not CHAPTERS:
    errors.append("A biblioteca não contém capítulos.")

for path, text in texts.items():
    headings = re.findall(r"^#{1,6} (.+)$", text, re.MULTILINE)
    seen = Counter()
    anchors[path] = set()
    if len(re.findall(r"^# ", text, re.MULTILINE)) != 1:
        errors.append(f"{path.relative_to(ROOT)}: esperado um título principal.")
    for heading in headings:
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        suffix = f"-{seen[slug]}" if seen[slug] else ""
        anchors[path].add(slug + suffix)
        seen[slug] += 1
    if path in CHAPTERS:
        for identifier in re.findall(r"^### (F\d+)\b", text, re.MULTILINE):
            if identifier in identifiers:
                errors.append(f"{identifier}: identificador repetido em {path.name}.")
            identifiers[identifier] = path

indexed = set()
for row in texts[INDEX].splitlines():
    if not row.startswith("| ["):
        continue
    destination = re.search(r"\]\(([^)]+)\)", row)
    if destination is None:
        continue
    chapter = (INDEX.parent / unquote(urlsplit(destination[1]).path)).resolve()
    for match in re.finditer(r"\bF(\d+)(?: a F(\d+))?\b", row.split("|")[-2]):
        first = int(match[1])
        last = int(match[2]) if match[2] else first
        if last < first:
            errors.append(f"Índice: intervalo invertido {match[0]}.")
        for number in range(first, last + 1):
            identifier = f"F{number:02d}"
            if identifier in indexed:
                errors.append(f"Índice: identificador repetido {identifier}.")
            indexed.add(identifier)
            if identifiers.get(identifier) != chapter:
                errors.append(f"Índice: {identifier} não pertence a {chapter.name}.")

if indexed != set(identifiers):
    errors.append(f"Índice e capítulos divergem: {sorted(indexed ^ set(identifiers))}.")

for path, text in texts.items():
    for href in re.findall(r"\]\(([^)\s]+)\)", text):
        parts = urlsplit(href)
        if parts.scheme or parts.netloc:
            continue
        link_count += 1
        target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
        if not target.is_file():
            errors.append(f"{path.relative_to(ROOT)}: destino ausente {href}.")
        elif parts.fragment:
            if target not in anchors:
                headings = re.findall(r"^#{1,6} (.+)$", target.read_text(encoding="utf-8"), re.MULTILINE)
                anchors[target] = {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}
            if unquote(parts.fragment) not in anchors[target]:
                errors.append(f"{path.relative_to(ROOT)}: âncora ausente {href}.")

if errors:
    sys.exit("\n".join(errors))
print(f"OK: {len(DOCUMENTS)} arquivos, {len(identifiers)} fragmentos e {link_count} links locais.")
print("Conferência estrutural. A qualidade de redação exige os cenários de composição.")
