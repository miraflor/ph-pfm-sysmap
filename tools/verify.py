"""Local reproducibility/diagram-contract checks. No external Python packages.

Run from any working directory: python tools/verify.py
Run after python tools/build.py so all outputs are up to date.

This does NOT check whether assertions about agencies are true in the real world.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pfmmap.model import Model  # noqa: E402
from pfmmap.petri import build_seq, soundness  # noqa: E402
from pfmmap.validate import check  # noqa: E402

ROOT = HERE.parent


def ensure(condition, message):
    if not condition:
        raise AssertionError(message)


def audit():
    m = Model(ROOT)
    errors, warnings = check(m)
    ensure(not errors, 'register validation errors: ' + '; '.join(errors[:5]))
    with (ROOT / 'audit/claim_reviews.csv').open(newline='', encoding='utf-8') as stream:
        rs = list(csv.DictReader(stream))
    keys = set()
    for r in rs:
        key = (r['entity_type'], r['entity_id'])
        ensure(key not in keys, f'duplicate audit id: {key}')
        keys.add(key)
        ensure(r['entity_type'] in ('node', 'flow', 'record'), f'bad audit entity type {key}')
        table, field = {'node': ('nodes', 'node_id'), 'flow': ('flows', 'flow_id'), 'record': ('records', 'record_id')}[r['entity_type']]
        ensure(any(x[field] == r['entity_id'] for x in m.t[table]), f'audit entity absent: {key}')
        ensure(r['source_code'] in m.ix['sources'], f'unknown audit source {r["source_code"]}')
        ensure(r['result'] in {'corroborated','qualified','needs_evidence','model_inference'}, f'bad review status: {key}')
        ensure(r['reviewed_on'] and r['scope'] and r['finding'], f'incomplete audit row: {key}')
        if r['result'] == 'corroborated':
            ensure(r['url'].startswith('https://'), f'corroborated claim requires primary source URL: {key}')
    from verification_inventory import build as build_review_queue
    inventory=build_review_queue()
    ensure(len(inventory) == len(m.t['nodes']) + len(m.t['flows']), 'review inventory is incomplete')
    # No current-operational status may be inferred from a planning document alone.
    weak = []
    for table, col in [('nodes','status'),('flows','stage')]:
        for r in m.t[table]:
            if r[col] in ('in_use','in_use_part') and m.evidence(r['basis'])['best'] in ('plan', 'inference','general_knowledge'):
                weak.append((table, next(iter(r.values())), r[col]))
    ensure(not weak, f'unsubstantiated live-use flags from plans/inference alone: {weak}')
    print(f'OK: {len(m.t["nodes"])} nodes / {len(m.t["flows"])} flows / {len(rs)} targeted claim reviews')
    print(f'    {len(warnings)} pre-existing registry warnings (not factual validation)')
    return m


def check_pnml(path: Path):
    # Namespaces and parsed XML verified, endpoints bipartite and readable.
    xml = ET.parse(path).getroot()
    ensure(xml.tag.endswith('pnml'), f'not PNML: {path}')
    ns = {'p': 'http://www.pnml.org/version-2009/grammar/pnml'}
    pages = xml.findall('.//p:page', ns)
    ensure(len(pages) == 1, f'incorrect page count: {path}')
    page = pages[0]
    places = {p.get('id') for p in page.findall('p:place', ns)}
    trans = {t.get('id') for t in page.findall('p:transition', ns)}
    ensure(places and trans, f'empty PNML net: {path}')
    ensure(not places.intersection(trans), f'place/transition ID collision: {path}')
    seen_ids = set()
    for a in page.findall('p:arc', ns):
        ensure(a.get('id') not in seen_ids, f'arc id duplicated: {path}')
        seen_ids.add(a.get('id'))
        ends = {a.get('source'),a.get('target')}
        ensure(len(ends & places) == 1 and len(ends & trans) == 1,
               f'arc not bipartite or dangling in {path}: {ends}')
    ensure(seen_ids, f'no arcs: {path}')
    return len(places), len(trans)


def diagrams(m):
    pnmls = sorted((ROOT/'petri').rglob('*.pnml'))
    ensure(len(pnmls) == 47, f'expected 27 curated+20 sequence PNML files, found {len(pnmls)}')
    for p in pnmls: check_pnml(p)
    ensure(len(list((ROOT/'petri/sequences').glob('*.pnml'))) == len(m.sequences), 'sequence PNML count differs from extracted diagrams')
    for sid in m.sequences:
        result = soundness(build_seq(m, sid))
        ensure(result.get('checked') and result.get('sound'), f'generated workflow net {sid} not sound: {result}')
    pumls = sorted((ROOT/'iconix').rglob('*.puml'))
    ensure(len(pumls) == 62, f'expected 62 PlantUML source files, found {len(pumls)}')
    for p in pumls:
        t = p.read_text(encoding='utf-8')
        ensure(t.count('@startuml') == t.count('@enduml') == 1, f'PlantUML wrapper problem: {p}')
    dots = sorted((ROOT/'maps').rglob('*.dot')) + sorted((ROOT/'petri').rglob('*.dot'))
    ensure(dots, 'no Graphviz DOT source files')
    ensure(shutil.which('dot'), 'graphviz dot executable unavailable')
    for p in dots:
        result = subprocess.run(['dot','-Tsvg'],input=p.read_bytes(),capture_output=True,timeout=80)
        ensure(result.returncode == 0 and b'<svg' in result.stdout, f'Graphviz cannot render {p}: {result.stderr[:250]}')
    svgs = sorted((ROOT/'maps').rglob('*.svg')) + sorted((ROOT/'petri').rglob('*.svg'))
    ensure(len(svgs) == len(dots), f'DOT/SVG count mismatch: {len(dots)} sources and {len(svgs)} SVGs')
    for p in svgs:
        ensure(ET.parse(p).getroot().tag.endswith('svg'), f'invalid SVG: {p}')
    print(f'OK: {len(pnmls)} PNMLs (bipartite), {len(m.sequences)} sound generated sequence nets')
    print(f'    {len(pumls)} PlantUML sources; {len(dots)} DOT render checks + valid SVG pairs')
    icons = list((ROOT/'iconix').rglob('*.svg'))
    if len(icons) < len(pumls):
        print(f'WARN: {len(icons)}/{len(pumls)} PlantUML SVGs present; set PLANTUML_JAR and rebuild to render the rest')
    else:
        for p in icons: ensure(ET.parse(p).getroot().tag.endswith('svg'), f'invalid PlantUML SVG: {p}')


def graphml(m):
    from export_graphml import make
    path = ROOT / "exports/pfm_flows.graphml"
    make(path)
    xml = ET.parse(path).getroot()
    ns={"g": "http://graphml.graphdrawing.org/xmlns"}
    count_nodes = len(xml.findall(".//g:node", ns))
    count_edges = len(xml.findall(".//g:edge", ns))
    expected_edges = sum(2 if f["via_id"] else 1 for f in m.t["flows"])
    ensure(count_nodes == len(m.t["nodes"]) and count_edges == expected_edges, "GraphML count mismatch")
    print(f"OK: GraphML exported {count_nodes} nodes and {count_edges} flow segments")

def consistency(m):
    doc = (ROOT/'docs/index.html').read_text(encoding='utf-8')
    ensure('<!doctype html>' in doc and 'window.PFM = ' in doc, 'site build missing')
    ensure('id="theme-toggle"' in doc and 'theme-button' in doc, 'theme control missing in compiled page')
    ensure('prefers-color-scheme: dark' not in doc, 'system dark preference still controls page')
    ensure('claim_reviews' in doc and 'Public source corroborates' in doc, 'claim review not integrated in published page')
    ensure('color-scheme: light;' in doc, 'light palette not explicitly default')
    ensure((ROOT/'docs/EVIDENCE_REVIEW.md').read_bytes() == (ROOT/'EVIDENCE_REVIEW.md').read_bytes(), 'site audit summary stale')
    baseline = hashlib.sha256((ROOT/'docs/index.html').read_bytes()).hexdigest()
    out = subprocess.run([sys.executable, str(HERE/'build.py'), '--page-only'], cwd=ROOT, capture_output=True, text=True,timeout=150)
    ensure(out.returncode == 0, f'page rebuild failed: {out.stderr[-800:]} {out.stdout[-800:]}')
    again = hashlib.sha256((ROOT/'docs/index.html').read_bytes()).hexdigest()
    ensure(baseline == again, 'page not reproducible: rebuilt SHA differs from checked-in output')
    print('OK: light-default UI, review panel, and deterministic GitHub Pages output (' + baseline[:16] + '…)')


def main():
    m = audit()
    diagrams(m)
    graphml(m)
    consistency(m)
    print('PASS — structural and reproduction checks, not independent operational certification')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, OSError, subprocess.TimeoutExpired) as e:
        print('FAIL:', e, file=sys.stderr)
        sys.exit(1)
