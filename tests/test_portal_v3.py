"""V3 semantic regression tests; run after python tools/build.py.

Uses actual repository registers and generated artifacts rather than testing only template text.
"""
from __future__ import annotations

import ast
import csv
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import portal  # noqa: E402


def split_ids(text: str) -> list[str]:
    return [x.strip() for x in (text or '').split(';') if x.strip()]


class ExpandedModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = portal.compile_payload(ROOT, '2026-10-13')

    def test_actor_mapping_is_exported_from_real_register(self):
        with (ROOT / 'model' / 'actor_map.csv').open(newline='', encoding='utf-8-sig') as fh:
            expected = list(csv.DictReader(fh))
        self.assertEqual(self.payload['actor_map'], expected)
        self.assertGreater(len(expected), 0)
        steps = self.payload['steps']
        names = {a['atlas_actor'] for a in expected}
        self.assertTrue(any(s.get('who_atlas') in names or s.get('to_atlas') in names for s in steps),
                        'no actor names in model match any sequence steps')

    def test_record_holder_join_from_real_registers(self):
        records = {r['record_id'] for r in self.payload['records']}
        places = {p['place_id']: p for p in self.payload['places']}
        nodes = {n['node_id'] for n in self.payload['nodes']}
        joined = 0
        for holder in self.payload['place_holders']:
            self.assertIn(holder['place_id'], places)
            for nid in split_ids(holder['held_in']):
                self.assertIn(nid, nodes)
            if records.intersection(split_ids(places[holder['place_id']]['records'])):
                joined += 1
        self.assertGreater(joined, 0, 'no real record connects to a modelled holder')

    def test_every_direct_basis_register_reaches_payload(self):
        for name in portal.DATA_TABLES:
            with self.subTest(register=name):
                csv_path = ROOT / 'model' / (name + '.csv')
                with csv_path.open(newline='', encoding='utf-8-sig') as stream:
                    rows = list(csv.DictReader(stream))
                self.assertEqual(self.payload[name], rows)

    def test_reproducible_mirrored_graphviz_assets(self):
        problems, _ = portal.audit_site(ROOT)
        self.assertFalse(problems, '; '.join(problems[:5]))
        for kind in ('petri', 'maps'):
            self.assertGreater(len(self.payload[kind]), 0)
            for drawing in self.payload[kind]:
                published = ROOT / 'docs' / drawing['path']
                source = ROOT / kind / Path(drawing['path']).relative_to('assets/' + kind)
                self.assertEqual(published.read_bytes(), source.read_bytes(), drawing['id'])

    def test_python39_grammar_for_fixed_petri_writer(self):
        source = (ROOT / 'tools' / 'pfmmap' / 'petri.py').read_text(encoding='utf-8')
        self.assertIn('DOT_NEWLINE', source)
        ast.parse(source, filename='tools/pfmmap/petri.py', feature_version=(3, 9))

    def test_mirror_detects_byte_level_divergence(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'maps').mkdir(parents=True)
            (root / 'docs' / 'assets' / 'maps').mkdir(parents=True)
            (root / 'maps' / 'L0.svg').write_text('<svg><!--version A--></svg>', encoding='utf-8')
            (root / 'docs' / 'assets' / 'maps' / 'L0.svg').write_text('<svg><!--version B--></svg>', encoding='utf-8')
            (root / 'docs' / 'index.html').write_text(
                '<script id="portal-payload" type="application/json">'
                '{"petri":[],"iconix":[],"maps":[{"path":"assets/maps/L0.svg","rendered":true}]}'
                '</script>', encoding='utf-8')
            problems, _ = portal.audit_site(root)
            self.assertTrue(any('differs' in p for p in problems), problems)


if __name__ == '__main__':
    unittest.main()
