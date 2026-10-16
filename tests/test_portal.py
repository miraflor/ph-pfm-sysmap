"""Tests of the research portal. Run after a full python tools/build.py.

  python -m unittest discover -s tests -p test_portal.py -v
"""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import portal  # noqa: E402
from portal import audit_site, build, compile_payload, decode_plantuml_text, drawing_inventory, svg_matches_source  # noqa: E402

AS_OF = '2026-10-13'


def encode_plantuml(text: str) -> str:
    """The text encoding of PlantUML (raw DEFLATE, then PlantUML's base64 alphabet), for the tests."""
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    data = c.compress(text.encode('utf-8')) + c.flush()
    a = portal._PLANTUML_ALPHABET
    out = []
    for i in range(0, len(data), 3):
        b = data[i:i + 3] + bytes(3 - len(data[i:i + 3]))
        out.append(a[b[0] >> 2] + a[((b[0] & 3) << 4) | (b[1] >> 4)] + a[((b[1] & 15) << 2) | (b[2] >> 6)] + a[b[2] & 63])
    return ''.join(out)


def old_style_svg(source: str) -> str:
    """An SVG as PlantUML 1.2019 writes it: the source in a trailing comment, with "--" written "- -"."""
    return '<svg><g><text>x</text><!--MD5=[0]\n' + source.replace('--', '- -') + '\n\nPlantUML version 1.2019.06\n--></g></svg>'


def tree_digest(folder: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(folder.rglob('*')):
        if f.is_file():
            h.update(f.relative_to(folder).as_posix().encode() + b'\0' + f.read_bytes())
    return h.hexdigest()


class PlantUmlProvenance(unittest.TestCase):
    """The check that decides whether an ICONIX drawing is shown."""
    SOURCE = '@startuml\nactor A\nA -- B\nB --> C : "x--y"\n@enduml\n'

    def test_known_encoding(self):
        # The example of the PlantUML documentation.
        self.assertEqual(decode_plantuml_text('SyfFKj2rKt3CoKnELR1Io4ZDoSa70000'), 'Bob -> Alice : hello')

    def test_comment_form(self):
        self.assertTrue(svg_matches_source(self.SOURCE, old_style_svg(self.SOURCE)))
        self.assertFalse(svg_matches_source(self.SOURCE.replace('actor A', 'actor Z'), old_style_svg(self.SOURCE)))

    def test_encoded_form(self):
        svg = f'<?xml version="1.0"?><?plantuml 1.2024.7?><?plantuml-src {encode_plantuml(self.SOURCE)}?><svg/>'
        self.assertTrue(svg_matches_source(self.SOURCE, svg))
        self.assertFalse(svg_matches_source(self.SOURCE + "' changed\n", svg))

    def test_no_embedded_source_is_undecided(self):
        self.assertIsNone(svg_matches_source(self.SOURCE, '<svg><g/></svg>'))

    def test_stale_and_unverified_drawings_are_withheld(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'iconix' / 'sequence').mkdir(parents=True)
            for name, svg in (('current', old_style_svg(self.SOURCE)), ('stale', old_style_svg(self.SOURCE.replace('A', 'Q'))),
                              ('silent', '<svg/>')):
                (root / 'iconix' / 'sequence' / f'{name}.puml').write_text(self.SOURCE, encoding='utf-8')
                (root / 'iconix' / 'sequence' / f'{name}.svg').write_text(svg, encoding='utf-8')
            (root / 'iconix' / 'sequence' / 'nodrawing.puml').write_text(self.SOURCE, encoding='utf-8')
            drawings, copies, manifest = drawing_inventory(root)
            status = {d['id']: d['status'] for d in drawings['iconix']}
            self.assertEqual(status, {'current': 'embedded_source_match', 'stale': 'stale', 'silent': 'unverified', 'nodrawing': 'missing'})
            self.assertEqual([p for _, p in copies], ['assets/iconix/sequence/current.svg'])
            self.assertEqual(list(manifest), ['sequence/current.puml'])
            # A drawing without embedded source is trusted when this build drew it, and later through the manifest.
            fresh, _, manifest = drawing_inventory(root, fresh_iconix_svg=True)
            self.assertEqual({d['id']: d['status'] for d in fresh['iconix']}['silent'], 'rendered_this_build')
            self.assertEqual({d['id']: d['status'] for d in fresh['iconix']}['stale'], 'stale')
            portal.mirror(root, [], manifest)
            later, _, _ = drawing_inventory(root)
            self.assertEqual({d['id']: d['status'] for d in later['iconix']}['silent'], 'manifest_match')


class PortalOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (ROOT / 'docs' / 'index.html').read_text(encoding='utf-8')
        cls.visualizer = (ROOT / 'docs' / 'visualizer.html').read_text(encoding='utf-8')
        cls.data = compile_payload(ROOT, AS_OF)

    def test_portal_links_all_sections(self):
        for section in ('overview', 'architecture', 'processes', 'models', 'records', 'evidence', 'methods'):
            self.assertIn(f'data-view="{section}"', self.index)
        self.assertIn('visualizer.html#map', self.index)
        self.assertNotIn('__REPO_HOME__', self.index)

    def test_visualizer_kept_and_linked(self):
        self.assertIn('window.PFM = ', self.visualizer)
        self.assertIn('id="t-nets"', self.visualizer)
        self.assertIn('class="hub-link" target="_top"', self.visualizer)
        self.assertIn('classList.add("embedded")', self.visualizer)
        self.assertIn('findFromHash', self.visualizer)

    def test_registers_loaded(self):
        for table in ('nodes', 'flows', 'records', 'fields', 'steps', 'transitions', 'sources', 'reviews', 'gaps'):
            self.assertGreater(len(self.data[table]), 0, table)
        self.assertTrue(all('source' in p and 'source_path' in p and 'status' in p for p in self.data['iconix']))

    def test_every_drawing_is_published_or_explained(self):
        problems, withheld = audit_site(ROOT)
        self.assertEqual(problems, [])
        for d in self.data['iconix']:
            if d['rendered']:
                self.assertTrue((ROOT / 'docs' / d['path']).is_file(), d['id'])
            else:
                self.assertEqual(d['path'], '', d['id'])
                self.assertIn(d['status'], ('stale', 'unverified', 'missing'))
        self.assertEqual(len(withheld), sum(1 for d in self.data['iconix'] if not d['rendered']))
        self.assertEqual(len(self.data['petri']), len(list((ROOT / 'petri').rglob('*.svg'))))
        self.assertEqual(len(self.data['maps']), len(list((ROOT / 'maps').rglob('*.svg'))))
        self.assertTrue(all(m['title'] for m in self.data['maps']))

    def test_compile_payload_writes_nothing(self):
        before = tree_digest(ROOT / 'docs')
        compile_payload(ROOT, AS_OF)
        self.assertEqual(before, tree_digest(ROOT / 'docs'))

    def test_build_is_deterministic(self):
        before = (tree_digest(ROOT / 'docs' / 'assets'), hashlib.sha256((ROOT / 'docs' / 'index.html').read_bytes()).digest())
        build(ROOT, AS_OF, fresh_iconix_svg=False)
        after = (tree_digest(ROOT / 'docs' / 'assets'), hashlib.sha256((ROOT / 'docs' / 'index.html').read_bytes()).digest())
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
