"""Build the research portal (docs/index.html) from the same registers as the visualizer.

No external Python dependencies. The visualizer is built separately, as docs/visualizer.html. This module owns
docs/index.html and the drawing copies in docs/assets/ (GitHub Pages serves only docs/).

Two steps, kept apart so that tests can inspect the result without writing files:

  compile_payload()  reads the registers and decides which drawings may be published. It writes nothing.
  build()            copies the drawings to docs/assets/ and writes docs/index.html.

ICONIX drawings. A PlantUML SVG is published only when there is evidence that it was drawn from the current
.puml source. There are three kinds of evidence, tried in this order:

  1. The SVG holds its own source. PlantUML writes the source into every SVG it draws: older versions as a
     trailing XML comment (with "--" written as "- -"), newer versions as an encoded <?plantuml-src ...?>
     instruction. When this source is present, it decides: equal to the .puml file means current, different
     means stale. No Java is needed for this check.
  2. This build ran PlantUML (fresh_iconix_svg=True).
  3. docs/assets/iconix-render-manifest.json records the SHA-256 of the .puml and the .svg from an earlier
     verified build, and both still match.

Petri-net and map SVGs are drawn by Graphviz in every full build, so they are copied as they are.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import zlib
from pathlib import Path

REPO_SLUG = 'miraflor/ph-pfm-sysmap'
REPO_HOME = f'https://github.com/{REPO_SLUG}'
REPO = f'{REPO_HOME}/blob/main/'
DATA_TABLES = (
    'nodes', 'flows', 'records', 'fields', 'record_links', 'steps',
    'roles', 'chains', 'places', 'place_holders', 'transitions',
    'bindings', 'rules', 'cohorts', 'use_cases', 'gaps', 'sources',
    'actor_map',
    'vocab',
)
MIRRORED = ('petri', 'iconix', 'maps')
MANIFEST = 'iconix-render-manifest.json'


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ------------------------------------------------------------------ PlantUML provenance

_PLANTUML_ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
_PLANTUML_INDEX = {c: i for i, c in enumerate(_PLANTUML_ALPHABET)}


def decode_plantuml_text(encoded: str) -> str | None:
    """Decode the text encoding of PlantUML: raw DEFLATE, then base64 with PlantUML's own alphabet."""
    text = encoded.strip()
    if text.startswith('~h'):
        try:
            return bytes.fromhex(text[2:]).decode('utf-8')
        except ValueError:
            return None
    if text.startswith('~1'):
        text = text[2:]
    try:
        values = [_PLANTUML_INDEX[c] for c in text]
    except KeyError:
        return None
    raw = bytearray()
    for i in range(0, len(values), 4):
        c = values[i:i + 4] + [0] * (4 - len(values[i:i + 4]))
        raw += bytes(((c[0] << 2) | (c[1] >> 4), ((c[1] & 0xF) << 4) | (c[2] >> 2), ((c[2] & 0x3) << 6) | c[3]))
    try:
        return zlib.decompressobj(-15).decompress(bytes(raw)).decode('utf-8')
    except (zlib.error, UnicodeDecodeError):
        return None


def embedded_plantuml_source(svg_text: str) -> tuple[str | None, str]:
    """Return (source, form) as PlantUML stored it inside an SVG, or (None, 'absent')."""
    m = re.search(r'<\?plantuml-src\s+([^?\s]+)\s*\?>', svg_text)
    if m:
        decoded = decode_plantuml_text(m.group(1))
        if decoded is not None:
            return decoded, 'encoded'
    start = svg_text.rfind('@startuml')
    if start >= 0:
        opened = svg_text.rfind('<!--', 0, start)
        closed = svg_text.rfind('-->', 0, start)
        end = svg_text.find('@enduml', start)
        if opened >= 0 and closed < opened and end > start:
            return svg_text[start:end + len('@enduml')], 'comment'
    return None, 'absent'


def _normal(text: str) -> str:
    return '\n'.join(line.rstrip() for line in text.replace('\r\n', '\n').strip().split('\n'))


def _as_comment(text: str) -> set[str]:
    """XML comments may not contain "--". PlantUML writes "- -" instead; allow both ways of doing it."""
    once = text.replace('--', '- -')
    repeated = text
    while '--' in repeated:
        repeated = repeated.replace('--', '- -')
    return {once, repeated}


def svg_matches_source(puml_text: str, svg_text: str) -> bool | None:
    """True or False when the SVG holds its source; None when it holds none and the question stays open."""
    embedded, form = embedded_plantuml_source(svg_text)
    if embedded is None:
        return None
    if form == 'comment':
        return _normal(embedded) in {_normal(c) for c in _as_comment(puml_text)}
    return _normal(embedded) == _normal(puml_text)


# ------------------------------------------------------------------ drawing inventory

def _graph_title(dot_path: Path) -> str:
    """The label of the graph in a DOT file, which is the title drawn at the top of the map."""
    if not dot_path.exists():
        return ''
    for line in dot_path.read_text(encoding='utf-8').splitlines()[:4]:
        m = re.match(r'graph \[.*?\blabel="((?:[^"\\]|\\.)*)"', line)
        if m:
            return m.group(1).replace('\\"', '"')
    return ''


def drawing_inventory(root: Path, fresh_iconix_svg: bool = False) -> tuple[dict, list[tuple[Path, str]], dict]:
    """Decide what to publish. Returns (lists for the page, [(source file, published path)], new manifest)."""
    previous = {}
    manifest_path = root / 'docs' / 'assets' / MANIFEST
    if manifest_path.exists():
        try:
            previous = json.loads(manifest_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            previous = {}
    copies: list[tuple[Path, str]] = []
    petri, iconix, maps = [], [], []
    for svg in sorted((root / 'petri').rglob('*.svg')):
        rel = svg.relative_to(root / 'petri')
        published = 'assets/petri/' + rel.as_posix()
        copies.append((svg, published))
        petri.append({'id': svg.stem, 'path': published, 'pnml': 'petri/' + rel.with_suffix('.pnml').as_posix(),
                      'kind': 'sequence' if rel.parts[0] == 'sequences' else 'chain'})
    for svg in sorted((root / 'maps').rglob('*.svg')):
        rel = svg.relative_to(root / 'maps')
        published = 'assets/maps/' + rel.as_posix()
        copies.append((svg, published))
        maps.append({'id': svg.stem, 'path': published, 'dot': 'maps/' + rel.with_suffix('.dot').as_posix(),
                     'kind': 'domain' if rel.parts[0] == 'by_domain' else 'overview',
                     'title': _graph_title(svg.with_suffix('.dot'))})
    manifest = {}
    for puml in sorted((root / 'iconix').rglob('*.puml')):
        rel = puml.relative_to(root / 'iconix')
        key = rel.as_posix()
        svg = puml.with_suffix('.svg')
        source = puml.read_text(encoding='utf-8')
        if not svg.exists():
            status = 'missing'
        else:
            match = svg_matches_source(source, svg.read_text(encoding='utf-8'))
            if match is True:
                status = 'embedded_source_match'
            elif match is False:
                status = 'stale'
            elif fresh_iconix_svg:
                status = 'rendered_this_build'
            elif previous.get(key, {}).get('puml') == digest(puml) and previous[key].get('svg') == digest(svg):
                status = 'manifest_match'
            else:
                status = 'unverified'
        published = 'assets/iconix/' + rel.with_suffix('.svg').as_posix()
        ok = status in ('embedded_source_match', 'rendered_this_build', 'manifest_match')
        if ok:
            copies.append((svg, published))
            manifest[key] = {'puml': digest(puml), 'svg': digest(svg)}
        iconix.append({
            'id': puml.stem, 'group': rel.parts[0] if len(rel.parts) > 1 else 'overview',
            'path': published if ok else '', 'rendered': ok, 'status': status,
            'source': source, 'source_path': 'iconix/' + key,
        })
    return {'petri': petri, 'iconix': iconix, 'maps': maps}, copies, manifest


def compile_payload(root: Path, as_of: str, fresh_iconix_svg: bool = False, drawings: dict | None = None) -> dict:
    """Everything the page needs, as one JSON-ready dict. Reads files only."""
    root = Path(root)
    data = {k: read_csv(root / 'model' / (k + '.csv')) for k in DATA_TABLES}
    review_path = root / 'audit' / 'claim_reviews.csv'
    data['reviews'] = read_csv(review_path) if review_path.exists() else []
    if drawings is None:
        drawings, _, _ = drawing_inventory(root, fresh_iconix_svg)
    data.update(drawings)
    data['as_of'] = as_of
    data['repository'] = REPO
    data['repository_home'] = REPO_HOME
    return data


# ------------------------------------------------------------------ writing

def mirror(root: Path, copies: list[tuple[Path, str]], manifest: dict) -> None:
    """Replace docs/assets/{petri,iconix,maps} with exactly the files to publish, so nothing stale stays."""
    assets = root / 'docs' / 'assets'
    for folder in MIRRORED:
        shutil.rmtree(assets / folder, ignore_errors=True)
    for source, published in copies:
        target = root / 'docs' / published
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    assets.mkdir(parents=True, exist_ok=True)
    (assets / MANIFEST).write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def render_page(root: Path, data: dict) -> str:
    sources = Path(root) / 'tools' / 'portal_site'
    template = (sources / 'template.html').read_text(encoding='utf-8')
    css = (sources / 'style.css').read_text(encoding='utf-8')
    script = (sources / 'app.js').read_text(encoding='utf-8')
    # Escaping "<" keeps text from the registers from closing the script element.
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'), sort_keys=True).replace('<', '\\u003c')
    return (template.replace('/* PORTAL_STYLE */', css)
                    .replace('__REPO_HOME__', REPO_HOME)
                    .replace('/* PORTAL_DATA */', payload)
                    .replace('/* PORTAL_APP */', script))


def build(root: Path, as_of: str, fresh_iconix_svg: bool = False) -> int:
    root = Path(root)
    drawings, copies, manifest = drawing_inventory(root, fresh_iconix_svg)
    data = compile_payload(root, as_of, drawings=drawings)
    mirror(root, copies, manifest)
    page = render_page(root, data)
    target = root / 'docs' / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding='utf-8')
    return len(page.encode('utf-8'))


def read_payload(root: Path) -> dict | None:
    html = (Path(root) / 'docs' / 'index.html').read_text(encoding='utf-8')
    m = re.search(r'<script id="portal-payload" type="application/json">(.*?)</script>', html, re.S)
    return json.loads(m.group(1)) if m else None


def audit_site(root: Path) -> tuple[list[str], list[str]]:
    """Check the published portal. Returns (problems, withheld ICONIX drawings).

    A problem is a missing drawing copy, a copy that differs from its source, a leftover file in docs/assets,
    or an ICONIX drawing published although its embedded source differs from the .puml file.
    Used by tools/verify.py."""
    root = Path(root)
    data = read_payload(root)
    if data is None:
        return ['portal payload missing from docs/index.html'], []
    problems = []
    for kind, folder in (('petri', 'petri'), ('maps', 'maps')):
        for d in data.get(kind, []):
            copy = root / 'docs' / d['path']
            original = root / folder / Path(d['path']).relative_to('assets/' + folder)
            if not copy.is_file():
                problems.append(f'missing published drawing {d["path"]}')
            elif not original.is_file() or copy.read_bytes() != original.read_bytes():
                problems.append(f'published drawing differs from {folder}/: {d["path"]}')
    for d in data.get('iconix', []):
        if not d['rendered']:
            continue
        copy = root / 'docs' / d['path']
        puml = root / d['source_path']
        if not copy.is_file():
            problems.append(f'missing published ICONIX drawing {d["path"]}')
        elif svg_matches_source(puml.read_text(encoding='utf-8'), copy.read_text(encoding='utf-8')) is False:
            problems.append(f'published ICONIX drawing is older than its source: {d["path"]}')
    published = {d['path'] for k in ('petri', 'maps', 'iconix') for d in data.get(k, []) if d.get('path')}
    for folder in MIRRORED:
        for f in (root / 'docs' / 'assets' / folder).rglob('*'):
            if f.is_file() and f.relative_to(root / 'docs').as_posix() not in published:
                problems.append(f'unpublished leftover in docs/assets: {f.relative_to(root).as_posix()}')
    withheld = [f'{d["source_path"]} ({d["status"]})' for d in data.get('iconix', []) if not d['rendered']]
    return problems, withheld


if __name__ == '__main__':
    import sys
    from argparse import ArgumentParser
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    from build import AS_OF  # one date for every output
    ap = ArgumentParser(description='Write docs/index.html and docs/assets/ only.')
    ap.add_argument('--root', type=Path, default=here.parent)
    args = ap.parse_args()
    print(f'portal: {build(args.root, AS_OF) / 1024:.1f} KiB')
