/* Offline test of the portal script, with a small stand-in for the browser. No npm packages.
   Run after the Python build:  node tests/portal_js_regression.cjs
   It renders every view, every record, every chain and cohort, every workflow and every source, and checks that
   every internal link points to something that exists. */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'docs', 'index.html'), 'utf8');
const dataMatch = html.match(/<script id="portal-payload" type="application\/json">([\s\S]*?)<\/script>/);
assert(dataMatch, 'portal data is embedded');
const scripts = Array.from(html.matchAll(/<script>([\s\S]*?)<\/script>/g));
assert(scripts.length, 'portal script is embedded');
const app = scripts.at(-1)[1];
new vm.Script(app); // syntax
const D = JSON.parse(dataMatch[1]);

const element = () => ({ innerHTML: '', textContent: '', href: '', dataset: {}, classList: { add() {}, remove() {}, toggle() { return false; } },
  setAttribute() {}, addEventListener() {}, focus() {}, replaceChildren() {}, showModal() {}, close() {} });
const els = {};
const get = (id) => (els[id] = els[id] || element());
const documentStub = {
  documentElement: { dataset: {} },
  title: '',
  getElementById(id) { return id === 'portal-payload' ? { textContent: dataMatch[1] } : id === 'map-frame' ? null : get(id); },
  querySelector(s) { return s.startsWith('#') ? get(s.slice(1)) : null; },
  querySelectorAll() { return []; },
  addEventListener() {},
};
const callbacks = {};
const location = { hash: '' };
const sandbox = {
  document: documentStub, location, URLSearchParams, console,
  window: { addEventListener(k, cb) { callbacks[k] = cb; }, scrollTo() {} },
  history: { replaceState(_, __, h) { location.hash = h; } },
  localStorage: { setItem() {}, getItem() { return null; } },
};
vm.runInNewContext(app, sandbox, { timeout: 10000 });

const main = () => get('main').innerHTML;
function open(params) {
  location.hash = '#' + new URLSearchParams(params).toString();
  callbacks.hashchange();
  assert(main().includes('class="hero"'), 'rendered ' + location.hash);
  checkLinks(location.hash);
  return main();
}

// Every internal link must point to a view that exists and to an identifier of the registers.
const ids = (t, k) => new Set((D[t] || []).map((x) => x[k]));
const I = { records: ids('records', 'record_id'), flows: ids('flows', 'flow_id'), nodes: ids('nodes', 'node_id'), chains: ids('chains', 'chain_id'),
  ucs: ids('use_cases', 'use_case_id'), gaps: ids('gaps', 'gap_id'), sources: ids('sources', 'code') };
const VIEWS = new Set(['overview', 'architecture', 'processes', 'models', 'records', 'evidence', 'methods']);
const unescape = (s) => s.replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>');
let linkCount = 0;
function checkLinks(where) {
  for (const m of main().matchAll(/data-go="([^"]*)"/g)) {
    const p = new URLSearchParams(unescape(m[1]));
    const view = p.get('view'), id = p.get('id') || '', find = p.get('find'), chain = p.get('chain');
    linkCount++;
    assert(VIEWS.has(view), `${where}: link to unknown view ${m[1]}`);
    if (view === 'records' && id) assert(I.records.has(id), `${where}: unknown record ${id}`);
    if (find) assert(I.flows.has(find) || I.nodes.has(find), `${where}: map link to unknown ${find}`);
    if (chain) assert(I.chains.has(chain), `${where}: unknown chain ${chain}`);
    if (id.startsWith('uc:')) assert(I.ucs.has(id.slice(3)), `${where}: unknown use case ${id}`);
    if (id.startsWith('gap:')) assert(I.gaps.has(id.slice(4)), `${where}: unknown open question ${id}`);
    if (id.startsWith('source:')) assert(I.sources.has(id.slice(7)), `${where}: unknown source ${id}`);
    if (id.startsWith('src:')) assert(D.iconix.some((d) => d.source_path === id.slice(4)), `${where}: unknown PlantUML file ${id}`);
  }
  for (const m of main().matchAll(/data-drawing="([^"]*)"/g)) {
    assert(fs.existsSync(path.join(root, 'docs', unescape(m[1]))), `${where}: drawing file missing ${m[1]}`);
  }
}

for (const v of VIEWS) open({ view: v });
assert(main() && documentStub.title.includes('Method'), 'page title follows the view');

for (const r of D.records) assert(open({ view: 'records', id: r.record_id }).includes('Fields ·'), 'record ' + r.record_id);
for (const c of D.chains) for (const k of D.cohorts) open({ view: 'processes', chain: c.chain_id, cohort: k.cohort_id });
for (const s of new Set(D.steps.map((x) => x.diagram_id))) assert(open({ view: 'processes', mode: 'sequences', seq: s }).includes(`Diagram ${s}`));
for (const s of D.sources) assert(open({ view: 'evidence', id: 'source:' + s.code }).includes('Cited by'), 'source ' + s.code);
for (const g of D.gaps) assert(open({ view: 'evidence', id: 'gap:' + g.gap_id }).includes('Showing one open question'));
for (const t of ['gaps', 'reviews', 'sources']) open({ view: 'evidence', tab: t });
for (const u of D.use_cases) open({ view: 'models', kind: 'iconix', id: 'uc:' + u.use_case_id });
for (const c of D.chains) open({ view: 'models', kind: 'petri', id: 'petri:' + c.chain_id });
for (const k of ['petri', 'iconix', 'maps']) {
  const page = open({ view: 'models', kind: k });
  const shown = (page.match(/data-drawing=/g) || []).length;
  assert.strictEqual(shown, D[k].filter((d) => d.path).length, `every ${k} drawing with a file has a View button`);
}
assert(open({ view: 'models', kind: 'iconix', id: 'src:' + D.iconix[0].source_path }).includes('PlantUML source'));
// The source explorer must account for all registers with direct basis columns,
// not only nodes, flows, records and gaps.
const addedBasisSources = [
  ['record_links', 'GK', 'relationships between records'],
  ['place_holders', 'ROADMAP2024', 'modelled record holders (by cohort)'],
  ['cohorts', 'COA-GAS', 'agency cohorts'],
];
for (const [table, code, caption] of addedBasisSources) {
  if (!(D[table] || []).some((row) => String(row.basis || '').includes(code))) continue;
  const page = open({ view: 'evidence', tab: 'sources', id: 'source:' + code });
  assert(page.includes(caption), `${table} missing from source ${code} reverse citations`);
}
const nca = open({ view: 'records', id: 'R-NCA' });
assert(nca.includes('Petri-net places and modelled holders'), 'record place/holder explorer absent');
assert(nca.includes('Cohort'), 'no modelled holder cohort exposed for NCA');
const seqWithMappedActor = D.steps.find((s) => (D.actor_map || []).some((a) => a.atlas_actor === s.who_atlas));
assert(seqWithMappedActor, 'no sequence actor mapping found');
assert(open({ view: 'processes', mode: 'sequences', seq: seqWithMappedActor.diagram_id }).includes('Actor mappings'),
       'atlas actor mappings omitted from workflow view');
// The old homepage anchors must still lead to the original interactive application.
assert(html.includes("location.replace('visualizer.html' + location.hash)"), 'legacy fragment forwarding missing');
// Actually exercise the small URL-preserving handler in the visualizer with a simulated hash.
const visualizerCode = fs.readFileSync(path.join(root, 'tools', 'site', 'app.js'), 'utf8');
const start = visualizerCode.indexOf('const findFromHash = () => {');
const end = visualizerCode.indexOf('    findFromHash();', start);
assert(start >= 0 && end > start, 'deep-link handler missing');
const stub = { location: { hash: '#find=F032' }, window: {}, URLSearchParams,
  decodeURIComponent, encodeURIComponent, qValue: '', received: '',
  showTab() { stub.location.hash = '#map'; },
  $(id) { return { set value(v) { stub.qValue = v; } }; },
  runSearch(v) { stub.received = v; },
  history: { replaceState(_, __, h) { stub.location.hash = h; } } };
vm.runInNewContext(visualizerCode.slice(start, end) + '\nfindFromHash();', stub);
assert.strictEqual(stub.received, 'F032', 'deep link did not select target');
assert.strictEqual(stub.location.hash, '#find=F032', 'deep link was overwritten by #map');

const f = D.flows[0].flow_id;
assert(open({ view: 'architecture', find: f }).includes(`visualizer.html#find=${encodeURIComponent(f)}`), 'map link by identifier');

console.log(`PASS: ${VIEWS.size} views, ${D.records.length} records, ${D.chains.length * D.cohorts.length} chain/cohort pairs, `
  + `${D.sources.length} sources, ${D.gaps.length} open questions; ${linkCount} internal links checked`);
