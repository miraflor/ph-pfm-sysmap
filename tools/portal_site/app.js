(() => {
  'use strict';
  const D = JSON.parse(document.getElementById('portal-payload').textContent);
  const $ = (s) => document.querySelector(s);
  const esc = (v) => String(v == null ? '' : v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  const list = (s) => String(s || '').split(';').map((x) => x.trim()).filter(Boolean);
  const by = (t, k) => Object.fromEntries((D[t] || []).map((x) => [x[k], x]));
  const N = by('nodes', 'node_id'), F = by('flows', 'flow_id'), R = by('records', 'record_id');
  const C = by('chains', 'chain_id'), U = by('use_cases', 'use_case_id'), S = by('sources', 'code');
  const RO = by('roles', 'role_id'), G = by('gaps', 'gap_id'), CO = by('cohorts', 'cohort_id');
  const VIEWS = ['overview', 'architecture', 'processes', 'models', 'records', 'evidence', 'methods'];
  const TITLES = { overview: 'Overview', architecture: 'Systems map', processes: 'Processes', models: 'Formal models', records: 'Records & data', evidence: 'Evidence', methods: 'Method' };
  const THEME_KEY = 'pfm-theme'; // the same key as the visualizer, so both pages keep one choice
  const drawn = D.iconix.filter((d) => d.rendered).length;

  // ------------------------------------------------------------ state, kept in the address (#...)
  // Every choice that changes what is shown is in the hash, so a view can be linked, bookmarked and reached with Back.
  const state = { view: 'overview', id: '', q: '', chain: '', cohort: 'P', mode: 'chains', seq: '', kind: 'petri', group: 'all', tab: 'gaps', find: '' };
  const PARAMS = ['view', 'id', 'chain', 'cohort', 'mode', 'seq', 'kind', 'group', 'tab', 'find'];
  const params = () => new URLSearchParams(location.hash.slice(1));
  function hashFor(next) {
    const p = new URLSearchParams();
    PARAMS.forEach((k) => { if (next[k]) p.set(k, next[k]); });
    return '#' + p.toString();
  }
  // Change some parameters of the current view. replace=true does not add a step to the browser history.
  function update(patch, replace) {
    const cur = Object.fromEntries(params().entries());
    const next = Object.assign({}, cur, patch);
    Object.keys(next).forEach((k) => { if (next[k] === '' || next[k] == null) delete next[k]; });
    const h = hashFor(next);
    if (h === location.hash) { route(); return; }
    if (replace) { history.replaceState(null, '', h); route(); } else location.hash = h;
  }

  // ------------------------------------------------------------ small HTML helpers
  const go = (paramsObj, label, cls = 'link-button', title = '') => `<button type="button" class="${cls}" data-go="${esc(new URLSearchParams(paramsObj).toString())}"${title ? ` title="${esc(title)}"` : ''}>${esc(label)}</button>`;
  const ext = (href, label) => `<a href="${esc(href)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`;
  const repo = (path, label) => ext(D.repository + path, label);
  const safeUrl = (u) => (/^https:\/\//i.test(u || '') ? u : '');
  const box = (body, cls = '') => `<section class="panel ${cls}">${body}</section>`;
  const stat = (n, l) => `<div class="stat"><b>${esc(n)}</b><span>${esc(l)}</span></div>`;
  const top = (title, sub, kicker) => `<div class="hero"><div class="eyebrow">${esc(kicker)}</div><h1>${esc(title)}</h1><p class="lead">${esc(sub)}</p></div>`;
  const opts = (rows, key, label, sel) => rows.map((r) => `<option value="${esc(r[key])}"${r[key] === sel ? ' selected' : ''}>${esc(r[label])}</option>`).join('');
  const searchInput = (placeholder) => `<input id="search" class="control search" type="search" value="${esc(state.q)}" placeholder="${esc(placeholder)}" aria-label="${esc(placeholder)}">`;
  const match = (...v) => !state.q || v.some((s) => String(s || '').toLowerCase().includes(state.q.toLowerCase()));
  const nodeName = (id) => (N[id] ? N[id].name : id);

  // A link for any identifier of the registers. Flows and boxes open the map; records, chains, use cases,
  // open questions and sources open their own view. Anything else stays plain text.
  function idLink(id) {
    if (R[id]) return go({ view: 'records', id }, id, 'chip', R[id].name);
    if (F[id]) return go({ view: 'architecture', find: id }, id, 'chip', `${F[id].what_passes} (show on the map)`);
    if (N[id]) return go({ view: 'architecture', find: id }, N[id].name, 'chip', `${N[id].full_name || N[id].name} (show on the map)`);
    if (C[id]) return go({ view: 'processes', chain: id }, id, 'chip', C[id].name);
    if (U[id]) return go({ view: 'models', kind: 'iconix', id: 'uc:' + id }, id, 'chip', U[id].name);
    if (G[id]) return go({ view: 'evidence', tab: 'gaps', id: 'gap:' + id }, id, 'chip', G[id].question);
    if (S[id]) return go({ view: 'evidence', tab: 'sources', id: 'source:' + id }, id, 'chip', S[id].title);
    return `<span class="tag">${esc(id)}</span>`;
  }
  const idLinks = (s) => list(s).map(idLink).join(' ');

  // Source codes inside a free-text basis ("NBC599, GAM-V1 Ch.3 s.10. Content: GK"). Every occurrence is found,
  // and a code never matches inside a longer code (GAA2026 inside GAA2026-GP).
  const reEsc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const CODES = Object.keys(S).filter(Boolean).sort((a, b) => b.length - a.length);
  const CODE_RE = CODES.length ? new RegExp('(^|[^A-Za-z0-9_-])(' + CODES.map(reEsc).join('|') + ')(?=[^A-Za-z0-9_-]|$)', 'g') : null;
  function codesIn(text) {
    const out = new Set();
    const raw = String(text || '');
    if (!CODE_RE) return [];
    CODE_RE.lastIndex = 0;
    let m;
    while ((m = CODE_RE.exec(raw))) {
      out.add(m[2]);
      CODE_RE.lastIndex = m.index + m[1].length + m[2].length;
    }
    return [...out];
  }
  // Chips for the codes, and the full text too when it says more than the codes (a section, a note).
  const srcChips = (text) => {
    const raw = String(text || '').trim();
    if (!raw) return '<span class="tiny">Not stated</span>';
    const codes = codesIn(raw);
    const chips = codes.map(idLink).join(' ');
    return codes.join(', ') === raw ? chips : `${chips} <span class="tiny">${esc(raw)}</span>`;
  };
  // Which rows of the registers cite each source code.
  let citations = null;
  function citedBy(code) {
    if (!citations) {
      citations = {};
      // All register arrays with a basis are indexed. Compound keys keep distinct
      // fields, cohort bindings and holder assignments distinct from one another.
      const keys = {
        nodes: r => r.node_id, flows: r => r.flow_id, records: r => r.record_id,
        gaps: r => r.gap_id, transitions: r => r.transition_id,
        places: r => r.place_id, bindings: r => `${r.transition_id}/${r.cohort}`,
        steps: r => r.step_id, fields: r => `${r.record_id}: ${r.field}`,
        record_links: r => r.link_id, place_holders: r => `${r.place_id}/${r.cohort}`,
        rules: r => r.rule_id, roles: r => r.role_id,
        use_cases: r => r.use_case_id, cohorts: r => r.cohort_id,
        chains: r => r.chain_id, actor_map: r => `${r.atlas_actor} → ${r.node_id || r.role_id}`,
      };
      Object.entries(keys).forEach(([table, key]) => (D[table] || []).forEach((row) => {
        if (!row.basis) return;
        for (const code of codesIn(row.basis)) {
          ((citations[code] = citations[code] || {})[table] = citations[code][table] || new Set()).add(String(key(row)));
        }
      }));
      (D.reviews || []).forEach((r) => { ((citations[r.source_code] = citations[r.source_code] || {}).reviews = citations[r.source_code].reviews || new Set()).add(r.entity_id); });
    }
    return citations[code] || {};
  }

  // ------------------------------------------------------------ views
  function overview() {
    const tiles = [
      ['architecture', 'Systems map', 'Institutions, systems, units and modules, and the flows between them. This is the original interactive map.'],
      ['processes', 'Processes', `The ${D.chains.length} curated chains, act by act for each cohort of agencies, and the ${new Set(D.steps.map((s) => s.diagram_id)).size} workflows of the atlas, step by step.`],
      ['models', 'Formal models', 'Petri nets, ICONIX diagrams and static maps, each with its source file.'],
      ['records', 'Records & data', 'Each record: its fields, linked records, flows, Petri-net places and modelled holders by agency cohort.'],
      ['evidence', 'Evidence', 'The sources, the claims reviewed one by one, and the open questions.'],
      ['methods', 'Method', 'How the outputs are built and checked, and what the checks cannot show.'],
    ];
    return `${top('Systems, flows, processes and records of Philippine PFM', 'This site brings together the outputs of the repository: the interactive map, the process chains, the Petri nets, the ICONIX models, the records and the sources. One set of registers (the CSV files in model/) makes all of them.', 'Philippine public financial management')}
    <div class="stats">${stat(D.nodes.filter((x) => x.type === 'system').length, 'systems')}${stat(D.flows.length, 'flows between bodies and systems')}${stat(D.records.length, 'records')}${stat(D.petri.length, 'Petri nets')}${stat(`${drawn} / ${D.iconix.length}`, 'ICONIX diagrams with a checked drawing')}</div>
    <h2>Parts of the site</h2>
    <div class="tiles">${tiles.map((t, i) => `<button type="button" class="tile" data-go="view=${t[0]}"><span class="number">0${i + 1}</span><strong>${esc(t[1])} →</strong><span>${esc(t[2])}</span></button>`).join('')}</div>
    <div class="grid-2 spaced">${box(`<h2>Start from one record</h2><p>Open the Notice of Cash Allocation (NCA): its fields, the flows that carry it, the Petri-net places that hold it, and the sources of each.</p>${go({ view: 'records', id: 'R-NCA' }, 'Open the NCA →', 'button secondary')}`)}
    ${box(`<h2>What the models do not show</h2><p>Each system and flow has a status (in use, planned, described, not stated) and its sources. The checks of the Petri nets are checks of the models: they do not show that the real processes work as drawn.</p>${go({ view: 'evidence' }, 'Open the evidence →', 'button secondary')}`)}</div>
    <p class="tiny">Registers as of ${esc(D.as_of)}.</p>`;
  }

  function architecture() {
    const find = state.find;
    const target = find ? `visualizer.html#find=${encodeURIComponent(find)}` : 'visualizer.html#map';
    const what = find ? (F[find] ? `flow ${find}: ${F[find].what_passes}` : N[find] ? N[find].name : find) : '';
    return `${top('Systems map', 'The original interactive map: three levels of detail, filters, cohorts, and the evidence of each box and line. Its tab Process nets draws the Petri nets.', 'Institutions, systems and flows')}
    <div class="inline-controls"><a class="button" href="${esc(target)}" target="_blank" rel="noopener noreferrer">Open the map on its own page ↗</a><a class="button secondary" href="visualizer.html#nets" target="_blank" rel="noopener noreferrer">Open the process nets ↗</a>${find ? go({ view: 'architecture' }, 'Show the whole map', 'button secondary') : ''}</div>
    ${find ? `<p class="small" role="status">The map shows ${esc(what)}.</p>` : ''}
    <iframe class="embed" id="map-frame" title="Interactive map of Philippine PFM systems" src="${esc(target)}"></iframe>
    <div class="notice"><strong>How to use the map:</strong> choose level 0, 1 or 2, use the filters and the search box, and click a box or a line to read about it. Inside this page the map has no header of its own; open it on its own page for the full screen.</div>`;
  }

  function chainNets(chainId) {
    return D.petri.filter((p) => p.kind === 'chain' && p.id.startsWith(chainId + '-'));
  }
  function drawingButton(d, title, label = 'View drawing', cls = 'button secondary') {
    return `<button type="button" class="${cls}" data-drawing="${esc(d.path)}" data-title="${esc(title)}">${esc(label)}</button>`;
  }
  function transitionItem(t) {
    const b = D.bindings.filter((x) => x.transition_id === t.transition_id && (x.cohort === 'all' || x.cohort === state.cohort));
    const bi = b.find((x) => x.cohort === state.cohort) || b[0];
    const steps = list(t.steps);
    return `<div class="timeline-item"><span class="tiny">${esc(t.transition_id)} · ${esc((RO[t.role_id] || {}).name || t.role_id)} · cohorts ${esc(t.cohorts)}</span><h3>${esc(t.name)}</h3>
      <p class="small">${esc((bi && bi.boundary) || t.note || '')}</p>
      ${bi && bi.writes_in ? `<div class="tiny">Writes in: ${idLinks(bi.writes_in)}</div>` : ''}
      ${steps.length ? `<div class="tiny">Steps of the atlas: ${esc(steps.join(', '))}</div>` : ''}</div>`;
  }
  function modeSwitch() {
    return `<div class="seg" role="group" aria-label="Kind of process">${['chains', 'sequences'].map((m) => `<button type="button" class="button ${state.mode === m ? '' : 'secondary'}" aria-pressed="${state.mode === m}" data-set="mode=${m}">${m === 'chains' ? 'Curated chains' : 'Workflows of the atlas'}</button>`).join('')}</div>`;
  }
  function flowItem(f) {
    return `<div class="result"><h3>${idLink(f.flow_id)} ${esc(f.what_passes)}</h3><p class="small">${idLink(f.from_id)} → ${f.via_id ? idLink(f.via_id) + ' → ' : ''}${idLink(f.to_id)} · ${esc(f.stage)}</p>${list(f.payload).length ? `<div class="tiny">Records: ${idLinks(f.payload)}</div>` : ''}</div>`;
  }
  function sequenceProcesses() {
    const ids = [...new Set(D.steps.map((s) => s.diagram_id).filter(Boolean))].sort();
    const selected = ids.includes(state.seq) ? state.seq : ids[0];
    const steps = D.steps.filter((s) => s.diagram_id === selected).sort((a, b) => Number(a.step) - Number(b.step));
    const flows = [...new Set(steps.flatMap((s) => list(s.flows)))].map((id) => F[id]).filter(Boolean);
    const net = D.petri.find((p) => p.kind === 'sequence' && p.id === selected);
    const actorNames = new Set(steps.flatMap((s) => [s.who_atlas, s.to_atlas]).filter(Boolean));
    const actors = (D.actor_map || []).filter((a) => actorNames.has(a.atlas_actor));
    return `${top('Workflows of the atlas', `The ${ids.length} sequence diagrams of the atlas, step by step: who sends what to whom, and the flows of the register that each step uses.`, 'Processes')}
    <div class="inline-controls">${modeSwitch()}<label for="sequence">Diagram</label><select id="sequence" class="control">${ids.map((id) => `<option value="${esc(id)}"${id === selected ? ' selected' : ''}>Diagram ${esc(id)}</option>`).join('')}</select></div>
    ${box(`<div class="row-head"><div><h2>Diagram ${esc(selected || '')}</h2><p class="small" data-count>${steps.length} steps · ${flows.length} flows of the register</p></div>${net ? drawingButton(net, `Workflow net of diagram ${selected}`, 'View the workflow net') : ''}</div>`)}
    <div class="grid-2"><section>${box(`<h2>Steps</h2><div class="timeline">${steps.map((st) => `<div class="timeline-item"><span class="tiny">${esc(st.step_id)} · ${esc(st.who_atlas || nodeName(st.who_node) || 'Actor not stated')}${st.to_atlas ? ' → ' + esc(st.to_atlas) : ''}${st.own_action === 'yes' ? ' · own action' : ''}</span><h3>${esc(st.text)}</h3>${st.section ? `<p class="small">${esc(st.section)}</p>` : ''}${st.block ? `<p class="tiny">Block: ${esc(st.block)}</p>` : ''}${st.flows ? `<div class="tiny">Flows: ${idLinks(st.flows)}</div>` : ''}</div>`).join('')}</div>`)}</section>
    <section>${box(`<h2>Flows of the register in this diagram · ${flows.length}</h2>${flows.map(flowItem).join('') || '<p class="small">No step of this diagram names a flow of the register. Documents can still pass; the register does not list them as flows between systems.</p>'}`)}
    ${box(`<h2>Actor mappings · ${actors.length}</h2><p class="small">Original atlas actor names matched to the model's institutions, units and roles.</p>
    ${actors.map((a) => `<div class="result"><strong>${esc(a.atlas_actor)}</strong><p class="small">${a.node_id ? idLink(a.node_id) : 'No mapped box'} · ${esc((RO[a.role_id] || {}).name || a.role_id || 'Role not stated')}</p>${a.note ? `<p class="tiny">${esc(a.note)}</p>` : ''}</div>`).join('') || '<p class="small">No actor mapping is registered for this diagram.</p>'}
    <p class="tiny">${repo('model/actor_map.csv', 'Actor mapping register ↗')}</p>`)}
    ${box(`<h2>Source of this workflow</h2><p class="small">The steps come from the sequence diagram of the atlas. The workflow net is made from these steps. That the net is sound (it can always finish, and finishes clean) is a property of the model, not of the real process.</p>${repo('model/steps.csv', 'Steps register ↗')} · ${net ? repo(net.pnml, 'PNML of the net ↗') : ''}`)}</section></div>`;
  }
  function processes() {
    if (state.mode === 'sequences') return sequenceProcesses();
    const selected = C[state.chain] || D.chains[0];
    if (!selected) return top('Processes', 'No chains are registered.', 'Processes');
    const cohort = CO[state.cohort] ? state.cohort : 'P';
    const transitions = D.transitions.filter((x) => x.chain_id === selected.chain_id && (x.cohorts === 'all' || list(x.cohorts).includes(cohort)));
    const cases = D.use_cases.filter((x) => x.chain_id === selected.chain_id);
    const stepIx = by('steps', 'step_id');
    const flows = [...new Set(transitions.flatMap((t) => list(t.steps)).flatMap((id) => list((stepIx[id] || {}).flows)))].map((id) => F[id]).filter(Boolean);
    const nets = chainNets(selected.chain_id);
    return `${top('Curated process chains', 'Choose a chain and a cohort of agencies. The page lists the acts in order, who does each act, where it is written, and the flows of the register that the acts use.', 'Processes')}
    <div class="inline-controls">${modeSwitch()}<label for="chain">Chain</label><select id="chain" class="control">${opts(D.chains, 'chain_id', 'name', selected.chain_id)}</select><label for="cohort">Cohort</label><select id="cohort" class="control">${opts(D.cohorts, 'cohort_id', 'name', cohort)}</select></div>
    ${box(`<div class="eyebrow">${esc(selected.chain_id)} · cohort ${esc(cohort)}</div><h2>${esc(selected.name)}</h2><p>${esc(selected.question)}</p><p class="small">${esc((CO[cohort] || {}).description || '')}</p><p class="tiny">In the atlas: ${esc(selected.atlas_ref)}</p>`)}
    <div class="grid-2"><section>${box(`<h2>Acts · ${transitions.length}</h2><div class="timeline">${transitions.length ? transitions.map(transitionItem).join('') : '<p class="empty">No act of this chain is registered for this cohort.</p>'}</div>`)}
    ${box(`<h2>Flows used by these acts · ${flows.length}</h2>${flows.length ? flows.map(flowItem).join('') : '<p class="small">No step of these acts names a flow of the register.</p>'}`)}</section>
    <section>${box(`<h2>Petri nets of this chain</h2>${nets.length ? `<div class="net-list">${nets.map((n) => `<div class="row-head"><span>${esc(n.id)}${n.id.endsWith('-' + cohort) ? ' <span class="tag">this cohort</span>' : ''}</span><span>${drawingButton(n, `${selected.name}: net ${n.id}`, 'View')} ${repo(n.pnml, 'PNML ↗')}</span></div>`).join('')}</div>` : '<p class="small">No net is exported for this chain.</p>'}<p class="tiny">${go({ view: 'models', kind: 'petri', id: 'petri:' + selected.chain_id }, 'All nets of this chain in the formal models →')}</p>`)}
    ${box(`<h2>System use cases · ${cases.length}</h2>${cases.length ? cases.map((u) => `<div class="result"><h3>${esc(u.name)}</h3><p class="small">${esc(u.goal)}</p><p class="tiny">${esc(u.use_case_id)} · acts ${esc(list(u.transitions).join(', '))}</p>${go({ view: 'models', kind: 'iconix', id: 'uc:' + u.use_case_id }, 'ICONIX diagrams of this use case →')}</div>`).join('') : '<p class="empty">No system use case is registered for this chain.</p>'}`)}</section></div>`;
  }

  const STATUS = {
    embedded_source_match: ['good', 'Drawing checked: it was made from the current source.'],
    rendered_this_build: ['good', 'Drawing made from the current source in this build.'],
    manifest_match: ['good', 'Drawing checked against a recorded earlier drawing of the same source.'],
    stale: ['warn', 'Drawing not shown: it was made from an older version of the source.'],
    unverified: ['warn', 'Drawing not shown: nothing shows that it matches the current source.'],
    missing: ['warn', 'No drawing yet; the source is available.'],
  };
  function drawingCard(d, kind) {
    const name = kind === 'maps' ? d.id.replace(/_/g, ' ') : (d.id || '').replace(/_/g, ' · ');
    let note, link, tag;
    if (kind === 'iconix') {
      const [cls, text] = STATUS[d.status] || ['', ''];
      note = `<p class="tiny ${cls}">${esc(text)}</p>`;
      link = repo(d.source_path, 'PlantUML source ↗');
      tag = d.group;
    } else if (kind === 'maps') {
      note = `<p class="tiny">${esc(d.title)}</p>`;
      link = repo(d.dot, 'DOT source ↗');
      tag = d.kind === 'domain' ? 'one part of PFM' : 'whole map';
    } else {
      note = `<p class="tiny">${d.kind === 'chain' ? 'Curated chain net' : 'Workflow net of a sequence diagram'} drawn by Graphviz.</p>`;
      link = repo(d.pnml, 'PNML source ↗');
      tag = d.kind;
    }
    const actions = [d.path ? drawingButton(d, name, 'View drawing', 'button') : '', kind === 'iconix' ? go({ view: 'models', kind: 'iconix', id: 'src:' + d.source_path }, 'Read source', 'button secondary') : ''].join(' ');
    return `<article class="drawing-card"><span class="tag">${esc(tag)}</span><h3>${esc(name)}</h3>${note}<div class="card-actions">${actions}</div><div class="tiny">${link}</div></article>`;
  }
  function models() {
    const kind = ['petri', 'iconix', 'maps'].includes(state.kind) ? state.kind : 'petri';
    const groups = { petri: ['all', 'chain', 'sequence'], iconix: ['all', 'overview', 'robustness', 'sequence'], maps: ['all', 'overview', 'domain'] }[kind];
    const groupOf = (x) => (kind === 'iconix' ? x.group : x.kind);
    const all = D[kind] || [];
    let items = all;
    let filter = '';
    if (state.id.startsWith('uc:') && kind === 'iconix') {
      const uc = state.id.slice(3);
      items = all.filter((x) => x.id.startsWith(uc + '_'));
      filter = `use case ${uc}${U[uc] ? ': ' + U[uc].name : ''}`;
    } else if (state.id.startsWith('petri:') && kind === 'petri') {
      const chain = state.id.slice(6);
      items = chainNets(chain);
      filter = `chain ${chain}${C[chain] ? ': ' + C[chain].name : ''}`;
    } else if (groups.includes(state.group) && state.group !== 'all') items = all.filter((x) => groupOf(x) === state.group);
    if (state.q) items = items.filter((x) => match(x.id, groupOf(x), x.title, x.source));
    const chosen = state.id.startsWith('src:') ? D.iconix.find((x) => x.source_path === state.id.slice(4)) : null;
    const label = { petri: `Petri nets (${D.petri.length})`, iconix: `ICONIX (${D.iconix.length})`, maps: `Static maps (${D.maps.length})` };
    return `${top('Formal models', 'Every drawing of the repository, with its source file. An ICONIX drawing is shown only when it is checked against its current PlantUML source; otherwise only the source is shown.', 'Petri nets · ICONIX · static maps')}
    <div class="inline-controls"><div class="seg" role="group" aria-label="Kind of model">${Object.keys(label).map((k) => `<button type="button" class="button ${kind === k ? '' : 'secondary'}" aria-pressed="${kind === k}" data-set="kind=${k}&group=&id=">${esc(label[k])}</button>`).join('')}</div>
    <select id="modelgroup" class="control" aria-label="Group">${groups.map((g) => `<option value="${esc(g)}"${(state.group || 'all') === g ? ' selected' : ''}>${esc(g === 'all' ? 'All groups' : g)}</option>`).join('')}</select>${searchInput('Find a model, use case, chain or diagram')}</div>
    ${filter ? `<p class="small">Showing only ${esc(filter)}. ${go({ view: 'models', kind }, 'Show all')}</p>` : ''}
    ${chosen ? box(`<div class="row-head"><h2>${esc(chosen.id)}: PlantUML source</h2>${repo(chosen.source_path, 'On GitHub ↗')}</div><p class="tiny ${(STATUS[chosen.status] || [''])[0]}">${esc((STATUS[chosen.status] || ['', ''])[1])}</p><pre><code>${esc(chosen.source)}</code></pre>`) : ''}
    ${kind === 'iconix' ? `<p class="small">${drawn} of ${D.iconix.length} ICONIX diagrams have a checked drawing.${drawn < D.iconix.length ? ' To draw the others, set PLANTUML_JAR and run the full build.' : ''}</p>` : ''}
    <p class="small" data-count>${items.length} model${items.length === 1 ? '' : 's'}</p>
    <div class="drawing-grid">${items.length ? items.map((d) => drawingCard(d, kind)).join('') : '<p class="empty">No model matches.</p>'}</div>`;
  }

  function recordDetail(r) {
    const fields = D.fields.filter((x) => x.record_id === r.record_id).sort((a, b) => Number(a.order) - Number(b.order));
    const links = D.record_links.filter((x) => x.from_record === r.record_id || x.to_record === r.record_id);
    const flows = D.flows.filter((x) => list(x.payload).includes(r.record_id));
    const places = D.places.filter((x) => list(x.records).includes(r.record_id));
    const reviews = D.reviews.filter((x) => x.entity_type === 'record' && x.entity_id === r.record_id);
    return `${box(`<div class="row-head"><h2>${esc(r.name)}</h2><span class="tag">${esc(r.record_id)}</span></div><p>${esc(r.purpose)}</p>
      <dl class="metadata"><dt>Kind</dt><dd>${esc(r.kind)}</dd><dt>Issuer</dt><dd>${esc(r.issuer || 'Not stated')}${r.issuer_node ? ' ' + idLink(r.issuer_node) : ''}</dd><dt>Form or identity</dt><dd>${esc([r.form_ref, r.identified_by].filter(Boolean).join(' · ') || 'Not stated')}</dd><dt>Sources</dt><dd>${srcChips(r.basis)}</dd>${r.atlas_ref ? `<dt>In the atlas</dt><dd>${esc(r.atlas_ref)}</dd>` : ''}</dl>
      ${r.note ? `<div class="detail">${esc(r.note)}</div>` : ''}${reviews.map((v) => `<p><span class="tag">Review: ${esc(v.result)}</span> ${esc(v.finding)}</p>`).join('')}`)}
    ${box(`<h2>Fields · ${fields.length}</h2>${fields.length ? `<div class="tablewrap"><table><thead><tr><th>Field</th><th>Type</th><th>Key</th><th>References</th></tr></thead><tbody>${fields.map((f) => `<tr><td>${esc(f.field)}</td><td>${esc(f.type)}</td><td>${esc(f.key)}</td><td>${f.references ? idLinks(f.references) : ''}</td></tr>`).join('')}</tbody></table></div>` : '<p class="small">No field is registered. This does not mean that the real record has no fields.</p>'}`)}
    ${box(`<h2>Links to other records · ${links.length}</h2>${links.length ? links.map((l) => { const other = l.from_record === r.record_id ? l.to_record : l.from_record; return `<div class="result">${go({ view: 'records', id: other }, (R[other] || {}).name || other)} <span class="small">${l.from_record === r.record_id ? '' : '(from) '}${esc(l.relation)} · ${esc(l.cardinality)}</span></div>`; }).join('') : '<p class="small">No link to another record is registered.</p>'}`)}
    ${box(`<h2>Flows that carry it · ${flows.length}</h2>${flows.length ? flows.map((f) => `<div class="result"><h3>${idLink(f.flow_id)} ${esc(f.what_passes)}</h3><p class="small">${idLink(f.from_id)} → ${idLink(f.to_id)} · ${esc(f.stage)}</p><div class="tiny">Sources: ${srcChips(f.basis)}</div></div>`).join('') : '<p class="small">No flow of the register carries this record.</p>'}`)}
    ${box(`<h2>Petri-net places and modelled holders · ${places.length}</h2>
    <p class="small">These are assignments within the models, by agency cohort where stated; they are not independent confirmation of the real deployment or official custody of a record.</p>
    ${places.map((p) => {
      const holders = (D.place_holders || []).filter((h) => h.place_id === p.place_id);
      return `<div class="result"><p><code>${esc(p.place_id)}</code> ${esc(p.name)} <span class="tiny">· ${esc(p.kind)} · cohorts ${esc(p.cohorts)}</span></p>
      ${holders.length ? `<dl class="metadata">${holders.map((h) => `<dt>Cohort ${esc(h.cohort)}</dt><dd>${idLinks(h.held_in) || '<span class="tiny">Not stated</span>'}${h.note ? `<p class="tiny">${esc(h.note)}</p>` : ''}<div class="tiny">Basis: ${srcChips(h.basis)}</div></dd>`).join('')}</dl>` : '<p class="tiny">No holder assignment is registered.</p>'}</div>`;
    }).join('') || '<p class="small">No place of the nets holds this record.</p>'}`)}`;
  }
  function records() {
    const rows = D.records.filter((r) => match(r.record_id, r.name, r.purpose, r.kind, r.form_ref)).sort((a, b) => a.name.localeCompare(b.name));
    const selected = R[state.id] || null;
    return `${top('Records & data', 'The documents, registries and messages of the model, with their fields, their links and the flows that carry them. An empty cell means that the registers do not say, not that the thing does not exist.', 'Records')}
    <div class="inline-controls">${searchInput('Find a record: NCA, ORS, voucher, form number…')}<span class="small" data-count>${rows.length} of ${D.records.length} records</span></div>
    <div class="grid-2 records-layout${selected ? ' has-detail' : ''}"><section class="record-list">${box(`<h2>Records</h2>${rows.map((r) => `<div class="result${selected && selected.record_id === r.record_id ? ' current' : ''}"><div class="row-head">${go({ view: 'records', id: r.record_id }, r.name)}<span class="tag">${esc(r.kind)}</span></div><p class="tiny">${esc(r.record_id)} · ${esc(r.purpose)}</p></div>`).join('') || '<p class="empty">No record matches.</p>'}`)}</section>
    <section class="record-detail">${selected ? recordDetail(selected) : box(`<h2>Choose a record</h2><p>Choose a record in the list to see its fields, links, flows and places. For an example, open the Notice of Cash Allocation.</p>${go({ view: 'records', id: 'R-NCA' }, 'Open the NCA →', 'button secondary')}`)}</section></div>`;
  }

  function evidence() {
    const groups = { gaps: 'Open questions', reviews: 'Claims reviewed', sources: 'Sources' };
    const tab = state.id.startsWith('source:') ? 'sources' : state.id.startsWith('gap:') ? 'gaps' : (groups[state.tab] ? state.tab : 'gaps');
    const source = state.id.startsWith('source:') ? S[state.id.slice(7)] : null;
    const gap = state.id.startsWith('gap:') ? G[state.id.slice(4)] : null;
    const rows = (D[tab] || []).filter((r) => (gap ? r === gap : match(...Object.values(r))));
    const item = (r) => {
      if (tab === 'gaps') return `<div class="result"><div class="row-head"><h3>${esc(r.question)}</h3><span class="tag ${r.status === 'open' ? 'warn' : ''}">${esc(r.status.replace(/_/g, ' '))}</span></div><p>${esc(r.why_it_matters)}</p><p class="tiny">${esc(r.gap_id)}</p>${r.related ? `<div class="tiny">Related: ${idLinks(r.related)}</div>` : ''}<details${gap ? ' open' : ''}><summary>Who could settle it, and how</summary><p>${esc(r.who_could_settle)}. ${esc(r.what_would_settle)}</p><div class="tiny">Sources: ${srcChips(r.basis)}</div></details></div>`;
      if (tab === 'reviews') {
        return `<div class="result"><div class="row-head"><h3>${esc(r.entity_type)} ${idLink(r.entity_id)}</h3><span class="tag">${esc(r.result.replace(/_/g, ' '))}</span></div><p>${esc(r.finding)}</p><p class="tiny">Scope: ${esc(r.scope)} · Reviewed ${esc(r.reviewed_on)}</p><div>${idLink(r.source_code)} ${safeUrl(r.url) ? ext(r.url, 'Reviewed document ↗') : ''}</div></div>`;
      }
      return `<div class="result"><div class="row-head"><h3>${go({ view: 'evidence', tab: 'sources', id: 'source:' + r.code }, r.title)}</h3><span class="tag">${esc(r.code)} · ${esc(r.type)}</span></div><p class="small">${esc(r.how_read)}</p>${safeUrl(r.url) ? ext(r.url, 'Open the source ↗') : ''}</div>`;
    };
    let sourceBox = '';
    if (source) {
      const cited = citedBy(source.code);
      const names = { nodes: 'boxes of the map', flows: 'flows', records: 'records',
        record_links: 'relationships between records', gaps: 'open questions',
        transitions: 'acts of the chains', places: 'Petri-net places',
        place_holders: 'modelled record holders (by cohort)',
        bindings: 'bindings of acts (by cohort)', steps: 'steps of the atlas',
        fields: 'fields of records', rules: 'rules', roles: 'roles',
        use_cases: 'system use cases', cohorts: 'agency cohorts', chains: 'process chains',
        actor_map: 'atlas actor mappings', reviews: 'claim reviews' };
      const linkable = ['nodes', 'flows', 'records', 'gaps', 'use_cases', 'chains'];
      const rowsCited = Object.keys(names).filter((t) => cited[t] && cited[t].size).map((t) => `<dt>${esc(names[t])} · ${cited[t].size}</dt><dd>${linkable.includes(t) ? [...cited[t]].map(idLink).join(' ') : `<span class="tiny">${esc([...cited[t]].join(', '))}</span>`}</dd>`).join('');
      sourceBox = box(`<div class="eyebrow">Source ${esc(source.code)} · ${esc(source.type)}</div><h2>${esc(source.title)}</h2><p>${esc(source.how_read)}</p>${source.used_for ? `<p class="small">Used for: ${esc(source.used_for)}</p>` : ''}${safeUrl(source.url) ? `<p>${ext(source.url, 'Open the source ↗')}</p>` : ''}<h3>Cited by</h3>${rowsCited ? `<dl class="metadata">${rowsCited}</dl>` : '<p class="small">No row of the registers cites this code in its basis.</p>'}`);
    }
    return `${top('Evidence', 'A public statement or a plan is not proof that a system works that way today. Each claim has its sources; some claims were reviewed one by one; what is not known is listed as an open question.', 'Sources and open questions')}
    <div class="inline-controls"><div class="seg" role="group" aria-label="Kind of evidence">${Object.entries(groups).map(([k, l]) => `<button type="button" data-set="tab=${k}&id=" class="button ${k === tab ? '' : 'secondary'}" aria-pressed="${k === tab}">${esc(l)} (${D[k].length})</button>`).join('')}</div>${gap ? '' : searchInput('Search the evidence, or a source code')}</div>
    ${sourceBox}
    ${gap ? `<p class="small">Showing one open question. ${go({ view: 'evidence', tab: 'gaps' }, 'Show all')}</p>` : ''}
    ${box(`<h2>${esc(groups[tab])} · <span data-count>${rows.length}</span></h2>${rows.map(item).join('') || '<p class="empty">Nothing matches.</p>'}`)}`;
  }

  function methods() {
    return `${top('Method', 'One set of CSV registers makes the map, the static maps, the Petri nets, the ICONIX models, the network export and this site. The programs check the structure of the models. Whether a claim is true of the real agencies is a question for the sources.', 'How the repository is built')}
    <div class="grid-2">${box(`<h2>1. Registers</h2><p>${D.nodes.length} boxes, ${D.flows.length} flows, ${D.records.length} records, ${D.fields.length} fields and ${D.steps.length} steps, in CSV files. Each row names its sources. What is not known is written as an open question.</p>${repo('docs/DATA_MODEL.md', 'Every column of the registers ↗')}`)}
    ${box(`<h2>2. Outputs</h2><p>Graphviz draws the static maps and the Petri nets (PNML, DOT, SVG). PlantUML text holds the ICONIX models. Two HTML pages, this site and the map, carry the registers inside them.</p>${repo('REPORT.md', 'Report of the last build ↗')}`)}
    ${box(`<h2>3. Checks</h2><p>The checks cover identifiers and allowed values, well-formed PNML, the soundness of the generated workflow nets, the rules of robustness diagrams, drawings checked against their sources, and pages that come out the same at every build. They do not certify that a real interface works.</p>${repo('REPRODUCIBILITY.md', 'How to build and check ↗')}`)}
    ${box(`<h2>4. Review of sources</h2><p>Each source has a type and says how it was read. Some claims were reviewed one by one against a public document. A status such as "in use" is not a verification of the real system.</p>${repo('EVIDENCE_REVIEW.md', 'Scope of the review ↗')}`)}</div>
    ${box(`<h2>Build it again</h2><pre><code>python tools/check.py\npython tools/build.py\npython tools/verify.py</code></pre><p class="small">The full build needs Python 3.9 or later and Graphviz. To draw the ICONIX diagrams again it also needs Java and PlantUML (the variable PLANTUML_JAR). Without PlantUML, the site checks each existing drawing against its source, shows the drawings that match, and shows only the source of the others.</p>${repo('tools/build.py', 'Build program ↗')} · ${ext(D.repository_home + '/tree/main/model', 'Registers ↗')}`)}
    <p class="tiny">This site and the map work without a network connection. Links to sources need one.</p>`;
  }

  // ------------------------------------------------------------ rendering and routing
  function applyThemeToMap() {
    const frame = document.getElementById('map-frame');
    if (!frame) return;
    try {
      const root = frame.contentDocument && frame.contentDocument.documentElement;
      if (!root) return;
      if (document.documentElement.dataset.theme === 'dark') root.setAttribute('data-theme', 'dark');
      else root.removeAttribute('data-theme');
    } catch (e) { /* a page opened from disk may not reach the frame; the map keeps its own choice */ }
  }
  function themeButton() {
    const dark = document.documentElement.dataset.theme === 'dark';
    $('#theme').textContent = dark ? 'Light mode' : 'Dark mode';
    $('#theme').setAttribute('aria-pressed', String(dark));
  }
  let lastView = null;
  function render() {
    const views = { overview, architecture, processes, models, records, evidence, methods };
    $('#main').innerHTML = `<div class="layout">${(views[state.view] || overview)()}</div>`;
    document.querySelectorAll('.nav button').forEach((b) => b.setAttribute('aria-current', b.dataset.view === state.view ? 'page' : 'false'));
    $('#stamp').textContent = `Registers as of ${D.as_of}`;
    document.title = `${TITLES[state.view]} · Philippine PFM systems and process models`;
    themeButton();
    const frame = document.getElementById('map-frame');
    if (frame) frame.addEventListener('load', applyThemeToMap);
  }
  function route() {
    const q = params();
    const v = q.get('view');
    state.view = VIEWS.includes(v) ? v : 'overview';
    if (state.view !== lastView) state.q = '';
    state.id = q.get('id') || '';
    state.chain = q.get('chain') || '';
    state.cohort = q.get('cohort') || 'P';
    state.mode = q.get('mode') === 'sequences' ? 'sequences' : 'chains';
    state.seq = q.get('seq') || '';
    state.kind = q.get('kind') || (state.id.startsWith('uc:') || state.id.startsWith('src:') ? 'iconix' : 'petri');
    state.group = q.get('group') || 'all';
    state.tab = q.get('tab') || 'gaps';
    state.find = q.get('find') || '';
    const changedView = lastView !== null && state.view !== lastView;
    lastView = state.view;
    render();
    window.scrollTo(0, 0);
    if (changedView) $('#content').focus({ preventScroll: true });
  }

  document.addEventListener('click', (e) => {
    const nav = e.target.closest('.nav [data-view]');
    if (nav) { const h = hashFor({ view: nav.dataset.view }); if (h === location.hash) route(); else location.hash = h; return; }
    const g = e.target.closest('[data-go]');
    if (g) { const h = '#' + g.dataset.go; if (h === location.hash) route(); else location.hash = h; return; }
    const s = e.target.closest('[data-set]');
    if (s) { update(Object.fromEntries(new URLSearchParams(s.dataset.set).entries())); return; }
    const pic = e.target.closest('[data-drawing]');
    if (pic) {
      const src = pic.dataset.drawing;
      if (!/^assets\/(petri|iconix|maps)\/[\w./-]+\.svg$/.test(src) || src.includes('..')) return;
      $('#drawing-title').textContent = pic.dataset.title;
      $('#drawing-link').href = src;
      const image = document.createElement('img');
      image.src = src;
      image.alt = pic.dataset.title;
      $('#drawing-body').classList.remove('actual');
      $('#drawing-size').textContent = 'Actual size';
      $('#drawing-body').replaceChildren(image);
      $('#drawing').showModal();
    }
  });
  document.addEventListener('change', (e) => {
    if (e.target.id === 'chain') update({ chain: e.target.value });
    if (e.target.id === 'cohort') update({ cohort: e.target.value });
    if (e.target.id === 'sequence') update({ seq: e.target.value });
    if (e.target.id === 'modelgroup') update({ group: e.target.value === 'all' ? '' : e.target.value, id: '' });
  });
  document.addEventListener('input', (e) => {
    if (e.target.id !== 'search') return;
    const pos = e.target.selectionStart;
    state.q = e.target.value;
    render();
    const el = $('#search');
    if (el) { el.focus(); el.setSelectionRange(pos, pos); }
    const count = document.querySelector('[data-count]');
    $('#live').textContent = count ? count.textContent : '';
  });
  $('#drawing-close').addEventListener('click', () => $('#drawing').close());
  $('#drawing').addEventListener('click', (e) => { if (e.target === $('#drawing')) $('#drawing').close(); });
  $('#drawing-size').addEventListener('click', () => {
    const actual = $('#drawing-body').classList.toggle('actual');
    $('#drawing-size').textContent = actual ? 'Fit to window' : 'Actual size';
  });
  $('#theme').addEventListener('click', () => {
    const dark = document.documentElement.dataset.theme === 'dark';
    if (dark) delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = 'dark';
    try { localStorage.setItem(THEME_KEY, dark ? 'light' : 'dark'); } catch (e) { /* storage can be blocked */ }
    themeButton();
    applyThemeToMap();
  });
  window.addEventListener('storage', (e) => {
    if (e.key !== THEME_KEY) return;
    if (e.newValue === 'dark') document.documentElement.dataset.theme = 'dark';
    else delete document.documentElement.dataset.theme;
    themeButton();
    applyThemeToMap();
  });
  window.addEventListener('hashchange', route);
  route();
})();
