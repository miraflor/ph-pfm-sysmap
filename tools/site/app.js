(function () {
  "use strict";
  const D = window.PFM;
  const ix = (arr, key) => Object.fromEntries(arr.map((x) => [x[key], x]));
  const N = ix(D.nodes, "node_id"), F = ix(D.flows, "flow_id"), R = ix(D.records, "record_id"), S = ix(D.sources, "code");
  const ST = ix(D.steps, "step_id"), G = ix(D.gaps, "gap_id"), PL = ix(D.places, "place_id"), TR = ix(D.transitions, "transition_id");
  const RO = ix(D.roles, "role_id"), RU = ix(D.rules, "rule_id"), CO = ix(D.cohorts, "cohort_id"), UC = ix(D.use_cases, "use_case_id");
  const CH = ix(D.chains_meta, "chain_id"), NETS = ix(D.nets, "id"), SEQ = ix(D.sequences, "id");
  const REV = Object.fromEntries((D.claim_reviews || []).map((x) => [x.entity_type + ":" + x.entity_id, x]));
  const V = {};
  D.vocab.forEach((v) => { (V[v.table + "." + v.column] = V[v.table + "." + v.column] || {})[v.value] = v.meaning; });
  const split = (s) => (s || "").split(";").map((x) => x.trim()).filter(Boolean);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const $ = (id) => document.getElementById(id);
  const cohortsOf = (v) => (!v || v === "all" ? ["P", "E", "B"] : split(v));

  // --------------------------------------------------------------- tokens of the theme
  const T = {};
  function readTokens() {
    const cs = getComputedStyle(document.documentElement);
    ["--bg", "--surface", "--raise", "--ink", "--muted", "--line", "--accent", "--authority", "--claim", "--cash", "--records", "--data", "--document",
      "--authority-soft", "--claim-soft", "--cash-soft", "--records-soft", "--warn", "--font-body", "--font-display", "--font-mono"].forEach((k) => { T[k] = cs.getPropertyValue(k).trim(); });
    T.group = {};
    ["budget", "procurement", "finance", "treasury", "revenue", "local", "audit", "planning", "ict", "banking", "spending", "political", "oversight", "governance", "other", "external"]
      .forEach((g) => { T.group[g] = cs.getPropertyValue("--g-" + g).trim(); });
  }
  readTokens();
  const KIND = () => ({ authority: T["--authority"], document: T["--document"], money: T["--cash"], data: T["--data"] });
  const LINE = () => ({ authority: T["--authority"], claim: T["--claim"], cash: T["--cash"], records: T["--records"] });
  const LINESOFT = () => ({ authority: T["--authority-soft"], claim: T["--claim-soft"], cash: T["--cash-soft"], records: T["--records-soft"] });

  const SHORT = {
    stage: { in_use: "In use", in_use_part: "In use for part", described_not_verified: "Described, use not verified", planned: "Planned", not_stated: "Not stated" },
    agent: { program: "Program to program", sender_person: "Sender's staff enter, upload or deliver", receiver_person: "Receiver's staff take it", own_person: "Own staff record it", not_stated: "Not stated", not_applicable: "Money or publication" },
    medium: { paper: "Paper", data_entry: "Typed or uploaded into a program", download: "Downloaded from a program", own_register: "Own register (paper or spreadsheet)", electronic_unspecified: "Electronic, kind not stated", api: "API (program interface)", payment_network: "Payment network", bank_transfer: "Bank transfer", cash_or_check: "Cash or check", public_website: "Public website", not_stated: "Not stated" },
    kind: { authority: "Authority", document: "Document", data: "Data", money: "Money" },
    domain: { planning_budget: "Planning and budget preparation", release: "Release", procurement: "Procurement", execution: "Obligation and payment", reporting: "Reporting", assets: "Assets", revenue: "Revenue and collections", treasury_debt: "Cash and debt", local: "Local governments", inside_agency: "Inside one agency", integration: "Planned IFMIS connections" },
    status: { in_use: "In use", in_use_part: "In use for part", described_not_verified: "Described, use not verified", planned: "Planned", retiring: "Being closed", required_by_law: "Required by law", not_stated: "Not stated in the sources" },
    ev: { record_instance: "published documents", law: "law", executive_issuance: "order of the President", budget_law: "budget law", rule: "circular, manual or rule", owner_statement: "statement of the owner", plan: "plan", assessment: "assessment", vendor: "vendor statement", press: "press report", inference: "inference", general_knowledge: "general knowledge", none: "no source" },
  };

  // --------------------------------------------------------------- helpers for the hierarchy
  const parentOf = (id) => N[id].parent_id || "";
  function ancestors(id) { const out = []; while (id) { out.unshift(id); id = parentOf(id); } return out; }
  const leaves = {};
  function leavesOf(id) {
    if (leaves[id]) return leaves[id];
    const n = N[id];
    leaves[id] = n.children.length ? n.children.flatMap(leavesOf) : [id];
    return leaves[id];
  }
  function countLine(id) {
    const n = N[id];
    if (!n.children.length) return "";
    const c = {};
    n.children.forEach((k) => { const t = N[k].type; c[t] = (c[t] || 0) + 1; });
    const name = { system: ["system", "systems"], unit: ["unit", "units"], module: ["module", "modules"], account: ["account", "accounts"], network: ["network", "networks"], standard: ["standard", "standards"], website: ["website", "websites"] };
    return Object.entries(c).map(([t, k]) => k + " " + (name[t] ? name[t][k === 1 ? 0 : 1] : t)).join(", ");
  }

  // --------------------------------------------------------------- sizes of labels
  // The label of a closed box is fitted to the box: the largest font size at which the text fits.
  const measure = document.createElement("canvas").getContext("2d");
  function linesNeeded(text, width, font) {
    measure.font = font;
    let total = 0;
    for (const line of text.split("\n")) {
      let cur = "", count = 1;
      for (const word of line.split(/\s+/).filter(Boolean)) {
        if (measure.measureText(word).width > width) return Infinity;
        const t = cur ? cur + " " + word : word;
        if (measure.measureText(t).width > width) { count += 1; cur = word; } else cur = t;
      }
      total += count;
    }
    return total;
  }
  function fitFont(text, w, h, maxFs, minFs) {
    for (let fs = maxFs; fs > minFs; fs -= 1) {
      if (linesNeeded(text, w - 24, `600 ${fs}px ${T["--font-display"]}`) * fs * 1.2 <= h - 12) return fs;
    }
    return minFs;
  }
  function focusOn(core, eles, pad, maxZ, animate) {
    if (!eles || !eles.length) return;
    const bb = eles.boundingBox();
    const w = core.width(), h = core.height();
    const z = Math.max(core.minZoom(), Math.min(maxZ, (w - 2 * pad) / Math.max(bb.w, 1), (h - 2 * pad) / Math.max(bb.h, 1)));
    const pan = { x: w / 2 - z * (bb.x1 + bb.w / 2), y: h / 2 - z * (bb.y1 + bb.h / 2) };
    core.stop(true, true);
    if (animate) core.animate({ zoom: z, pan }, { duration: 320 }); else core.viewport({ zoom: z, pan });
  }

  // --------------------------------------------------------------- map state
  const state = {
    level: 0, expanded: new Set(), cohort: "all", showSteps: false, showAdjacent: false,
    kind: new Set(Object.keys(SHORT.kind)), stage: new Set(Object.keys(SHORT.stage)), agent: new Set(Object.keys(SHORT.agent)),
    medium: new Set(Object.keys(SHORT.medium)), domain: new Set(Object.keys(SHORT.domain)), gkOnly: true, selected: null,
  };
  function setLevel(level) {
    state.level = level;
    state.selected = null;
    state.expanded = new Set();
    if (level >= 1) D.nodes.filter((n) => n.level === "0" && n.children.length).forEach((n) => state.expanded.add(n.node_id));
    if (level >= 2) D.nodes.filter((n) => n.level === "1" && n.children.length).forEach((n) => state.expanded.add(n.node_id));
    document.querySelectorAll("#levels button").forEach((b) => b.setAttribute("aria-pressed", String(+b.dataset.level === level)));
  }
  const compact = () => state.expanded.size === 0;
  const inScope = (id) => state.showAdjacent || N[id].scope !== "adjacent";
  function isVisible(id) { const a = ancestors(id); return a.slice(0, -1).every((x) => state.expanded.has(x)) && a.every(inScope); }
  function rep(id) {
    const a = ancestors(id);
    for (const x of a) { if (x === id || !state.expanded.has(x)) return x; }
    return id;
  }
  function flowVisible(f) {
    if (!state.kind.has(f.kind) || !state.stage.has(f.stage) || !state.agent.has(f.agent) || !state.medium.has(f.medium) || !state.domain.has(f.domain)) return false;
    if (state.cohort !== "all" && !cohortsOf(f.cohorts).includes(state.cohort)) return false;
    if (!state.gkOnly && f.ev.best === "general_knowledge") return false;
    const ends = [f.from_id, f.to_id].concat(f.via_id ? [f.via_id] : []);
    return ends.every((e) => ancestors(e).every(inScope));
  }
  const segments = (f) => (f.via_id ? [[f.from_id, f.via_id], [f.via_id, f.to_id]] : [[f.from_id, f.to_id]]);

  function edgeLook(f) {
    const dash = { paper: "dotted", data_entry: "dashed", download: "dashed", own_register: "dashed" }[f.medium] || "solid";
    const width = f.medium === "api" || f.medium === "payment_network" ? 3 : f.kind === "money" ? 2.4 : 1.7;
    const op = { planned: 0.55, described_not_verified: 0.72, not_stated: 0.85 }[f.stage] || 1;
    return { color: KIND()[f.kind], dash, width, op, hollow: f.stage === "planned" ? "hollow" : "filled" };
  }

  function buildElements() {
    const els = [];
    const vis = D.nodes.filter((n) => isVisible(n.node_id));
    const visSet = new Set(vis.map((n) => n.node_id));
    const edges = [];
    const agg = {};
    const flowsShown = D.flows.filter(flowVisible);
    const touched = new Set();
    flowsShown.forEach((f) => {
      segments(f).forEach(([a, b], si) => {
        const A = rep(a), B = rep(b);
        if (A === B) return;
        touched.add(A); touched.add(B);
        const collapsed = (x) => N[x].children.length && !state.expanded.has(x);
        if (collapsed(A) || collapsed(B)) {
          const k = A + "|" + B;
          (agg[k] = agg[k] || { A, B, flows: [] }).flows.push(f.flow_id);
        } else {
          const L = edgeLook(f);
          edges.push({ group: "edges", data: { id: "f:" + f.flow_id + ":" + si, source: A, target: B, flow: f.flow_id, label: f.flow_id, color: L.color, dash: L.dash, width: L.width, op: L.op, fill: L.hollow, etype: "flow" } });
        }
      });
    });
    Object.values(agg).forEach((g) => {
      const kinds = [...new Set(g.flows.map((x) => F[x].kind))];
      const color = kinds.length === 1 ? KIND()[kinds[0]] : T["--ink"];
      edges.push({ group: "edges", data: { id: "a:" + g.A + "|" + g.B, source: g.A, target: g.B, flows: g.flows, label: String(g.flows.length), color, dash: "solid", width: Math.min(1.6 + 0.7 * g.flows.length, 9), op: 0.9, fill: "filled", etype: "agg" } });
    });
    if (state.showSteps) {
      const sagg = {};
      D.steps.forEach((s) => {
        if (s.own_action === "yes" || !s.to_node || split(s.flows).length) return;
        if (!ancestors(s.who_node).every(inScope) || !ancestors(s.to_node).every(inScope)) return;
        const A = rep(s.who_node), B = rep(s.to_node);
        if (A === B) return;
        touched.add(A); touched.add(B);
        const k = A + "|" + B;
        (sagg[k] = sagg[k] || { A, B, steps: [] }).steps.push(s.step_id);
      });
      Object.values(sagg).forEach((g) => {
        edges.push({ group: "edges", data: { id: "s:" + g.A + "|" + g.B, source: g.A, target: g.B, steps: g.steps, label: g.steps.length > 1 ? String(g.steps.length) : "", color: T["--muted"], dash: "dashed", width: 1.2, op: 0.7, fill: "filled", etype: "steps" } });
      });
    }
    const filtering = state.cohort !== "all" || ["kind", "stage", "agent", "medium", "domain"].some((k) => state[k].size !== Object.keys(SHORT[k]).length) || !state.gkOnly;
    const cmp = compact();
    vis.forEach((n) => {
      const id = n.node_id;
      const compound = n.children.length && state.expanded.has(id) && n.children.some((k) => visSet.has(k));
      const collapsedParent = n.children.length && !state.expanded.has(id);
      let label = n.name;
      if (collapsedParent) label += "\n" + countLine(id);
      let w, h, fs, big = 0;
      if (compound) { w = n.fw; h = n.fh; fs = n.level === "0" ? 26 : 15; }
      else if (cmp) { w = 168; h = 64; fs = fitFont(label, w, h, 15, 9); big = 1; }
      else if (collapsedParent) { w = n.fw; h = n.fh; fs = fitFont(label, w, h, Math.round(Math.max(12, Math.min(30, h * 0.22))), 10); big = 1; }
      else if (n.level === "0") { w = 170; h = 54; fs = 13; big = 1; }
      else if (n.level === "1") { w = 156; h = 46; fs = 11; }
      else { w = 138; h = 38; fs = 10; }
      const d = { id, label, type: n.type, level: n.level, status: n.status || "none", scope: n.scope, fill: T.group[n.group] || T["--surface"],
        compound: compound ? 1 : 0, collapsed: collapsedParent ? 1 : 0, big, w, h, fs, tw: compound ? w : w - 24 };
      if (n.parent_id && visSet.has(n.parent_id)) d.parent = n.parent_id;
      const el = { group: "nodes", data: d, classes: [] };
      if (!compound) el.position = positionOf(id);
      if (filtering && !compound && !touched.has(id)) el.classes.push("faded");
      if (n.type === "unit") d.fill = T["--surface"];
      el.classes = el.classes.join(" ");
      els.push(el);
    });
    return els.concat(edges);
  }

  // Level 0 alone uses the compact layout. As soon as one box is open, the full layout is used, in which a closed
  // box takes the space of its contents, so that opening or closing a box does not move the other boxes.
  function positionOf(id) {
    const n = N[id];
    if (compact()) return { x: n.x0, y: n.y0 };
    if (n.x !== undefined) return { x: n.x, y: n.y };
    return { x: n.fx, y: n.fy };
  }

  function mapStyle() {
    return [
      { selector: "node", style: {
        label: "data(label)", "text-wrap": "wrap", "text-max-width": "data(tw)", "font-family": T["--font-body"], "font-size": "data(fs)", "line-height": 1.15,
        color: T["--ink"], "text-valign": "center", "text-halign": "center", shape: "round-rectangle", width: "data(w)", height: "data(h)",
        "background-color": "data(fill)", "border-width": 1, "border-color": T["--ink"], "border-opacity": 0.55, "min-zoomed-font-size": 5 } },
      { selector: "node[type = 'unit']", style: { shape: "rectangle" } },
      { selector: "node[type = 'account']", style: { shape: "barrel" } },
      { selector: "node[type = 'network']", style: { shape: "hexagon" } },
      { selector: "node[type = 'standard']", style: { shape: "tag" } },
      { selector: "node[type = 'external']", style: { "border-width": 1.5, "border-opacity": 0.8 } },
      { selector: "node[big = 1]", style: { "font-family": T["--font-display"], "font-weight": 600, "border-width": 1.6, "border-opacity": 0.7 } },
      { selector: "node[collapsed = 1]", style: { "border-width": 2, "border-opacity": 0.75 } },
      { selector: "node[compound = 1]", style: {
        "text-valign": "top", "text-halign": "center", "font-family": T["--font-display"], "font-weight": 600, "text-margin-y": -4,
        padding: 12, "background-opacity": 0.75, "border-width": 1, "border-opacity": 0.45, shape: "round-rectangle", "min-zoomed-font-size": 0 } },
      { selector: "node[status = 'planned']", style: { "border-style": "dashed", "border-width": 1.5 } },
      { selector: "node[status = 'retiring'], node[status = 'not_stated']", style: { "border-style": "dotted", "border-width": 1.6 } },
      { selector: "node[status = 'described_not_verified'], node[status = 'required_by_law']", style: { "border-color": T["--muted"] } },
      { selector: "node[scope = 'adjacent']", style: { opacity: 0.85 } },
      { selector: "edge", style: {
        "curve-style": "bezier", width: "data(width)", "line-color": "data(color)", "target-arrow-color": "data(color)", "target-arrow-shape": "triangle",
        "target-arrow-fill": "data(fill)", "arrow-scale": 0.9, "line-style": "data(dash)", opacity: "data(op)", label: "data(label)",
        "font-family": T["--font-mono"], "font-size": 9, color: T["--muted"], "text-background-color": T["--bg"], "text-background-opacity": 0.85,
        "text-background-padding": 1, "text-rotation": "autorotate", "min-zoomed-font-size": 6 } },
      { selector: "edge[etype = 'agg']", style: { "font-size": 12, color: T["--ink"], "font-family": T["--font-display"], "font-weight": 600 } },
      { selector: "edge[etype = 'steps']", style: { "line-dash-pattern": [2, 5] } },
      { selector: ".faded", style: { opacity: 0.25 } },
      { selector: "node.dim", style: { opacity: 0.28 } },
      { selector: "edge.dim", style: { opacity: 0.07 } },
      { selector: "node:selected", style: { "border-color": T["--accent"], "border-width": 3, "border-opacity": 1 } },
      { selector: "edge:selected", style: { "line-color": T["--accent"], "target-arrow-color": T["--accent"], width: 4, opacity: 1, "z-index": 10 } },
      { selector: ".hl", style: { "border-color": T["--accent"], "border-width": 3, "border-opacity": 1 } },
      { selector: "edge.hl", style: { "line-color": T["--accent"], "target-arrow-color": T["--accent"], opacity: 1 } },
    ];
  }

  let cy = null;
  let lastSpace = null;
  // Draw the map again. The viewport stays where it is, unless the layout changes between the compact level 0
  // and the full layout: then the view moves to the box that was opened, or to the whole map.
  function renderMap(opts) {
    opts = opts || {};
    const els = buildElements();
    if (!cy) {
      cy = cytoscape({ container: $("cy"), elements: [], style: mapStyle(), minZoom: 0.06, maxZoom: 3, boxSelectionEnabled: false });
      cy.on("tap", "node", (e) => { selectNode(e.target.id()); });
      cy.on("tap", "edge", (e) => { selectEdge(e.target); });
      cy.on("dbltap", "node", (e) => { toggleNode(e.target.id()); });
      cy.on("tap", (e) => { if (e.target === cy) { state.selected = null; highlight(null); panelOverview(); } });
    }
    const space = compact() ? "compact" : "full";
    const changed = lastSpace !== null && space !== lastSpace;
    lastSpace = space;
    const vp = { zoom: cy.zoom(), pan: Object.assign({}, cy.pan()) };
    cy.batch(() => { cy.elements().remove(); cy.add(els); });
    if (opts.fit) cy.fit(cy.elements(), 30);
    else if (changed) {
      const f = opts.focus ? cy.getElementById(opts.focus) : null;
      if (space === "full" && f && f.length) focusOn(cy, f.union(f.descendants()), 50, 1.0, false);
      else cy.fit(cy.elements(), 30);
    } else cy.viewport({ zoom: vp.zoom, pan: vp.pan });
    if (state.selected) {
      const el = cy.getElementById(state.selected);
      if (el && el.length) { el.select(); highlight(el); }
    }
  }
  // Fade what is not connected to the selected box or line.
  function highlight(ele) {
    if (!cy) return;
    cy.elements().removeClass("dim");
    if (!ele || !ele.length) return;
    let core;
    if (ele.isNode()) {
      const set = ele.union(ele.descendants());
      const eds = set.connectedEdges();
      core = set.union(eds).union(eds.connectedNodes());
    } else core = ele.union(ele.connectedNodes());
    core = core.union(core.nodes().ancestors());
    cy.elements().not(core).addClass("dim");
  }
  function toggleNode(id) {
    const n = N[id];
    if (!n.children.length) return;
    if (state.expanded.has(id)) {
      state.expanded.delete(id);
      D.nodes.filter((x) => ancestors(x.node_id).includes(id)).forEach((x) => state.expanded.delete(x.node_id));
    } else state.expanded.add(id);
    state.selected = id;
    renderMap({ focus: id });
    selectNode(id);
  }
  function revealNode(id) {
    ancestors(id).slice(0, -1).forEach((a) => state.expanded.add(a));
    if (N[id].scope === "adjacent") { state.showAdjacent = true; $("showAdjacent").checked = true; }
    state.selected = id;
    renderMap({ focus: id });
    const el = cy.getElementById(id);
    if (el.length) focusOn(cy, el.union(el.descendants()), 80, 1.1, true);
    selectNode(id);
  }
  function revealFlow(fid) {
    const f = F[fid];
    const ends = [f.from_id, f.to_id, f.via_id].filter(Boolean);
    // open the boxes around both ends, and an end that is itself a box with contents, so that the flow has its own line
    ends.forEach((e) => { ancestors(e).slice(0, -1).forEach((a) => state.expanded.add(a)); if (N[e].children.length) state.expanded.add(e); });
    if (ends.some((e) => ancestors(e).some((a) => N[a].scope === "adjacent"))) { state.showAdjacent = true; $("showAdjacent").checked = true; }
    const el0 = () => cy.edges().filter((e) => e.data("flow") === fid || (e.data("flows") || []).includes(fid));
    state.selected = null;
    renderMap({ focus: f.from_id });
    let el = el0();
    if (!el.length) {
      // the flow is hidden by a filter: show it anyway, with the filters reset
      resetFilters();
      state.cohort = "all"; $("cohort").value = "all";
      renderMap({});
      el = el0();
    }
    if (el.length) {
      state.selected = el[0].id();
      cy.elements().unselect();
      el.select();
      highlight(el);
      focusOn(cy, el.union(el.connectedNodes()), 70, 1.1, true);
    }
    panelFlow(fid);
  }

  // --------------------------------------------------------------- panel content
  function codesHtml(basis) {
    const codes = basis.codes || [];
    if (!codes.length) return '<span class="note">No source code</span>';
    return codes.map((c) => {
      const s = S[c];
      if (!s) return `<span class="src">${esc(c)}</span>`;
      const cls = s.type === "general_knowledge" ? "src gk" : "src";
      const tip = `${s.title} (${SHORT.ev[s.type] || s.type}). ${s.how_read}`;
      return s.url ? `<a class="${cls}" href="${esc(s.url)}" target="_blank" rel="noopener" title="${esc(tip)}">${esc(c)}</a>` : `<span class="${cls}" title="${esc(tip)}">${esc(c)}</span>`;
    }).join(" ");
  }
  function evLine(ev, basisText) {
    const best = SHORT.ev[ev.best] || ev.best;
    return `<dt>Strongest source</dt><dd>${esc(best)}${ev.gk ? ' <span class="pill gk">part is general knowledge</span>' : ""}</dd><dt>Basis</dt><dd>${esc(basisText)}<br>${codesHtml(ev)}</dd>`;
  }
  const nodeLink = (id) => (N[id] ? `<button class="linklike" data-node="${esc(id)}">${esc(N[id].name)}</button>` : esc(id));
  const flowLink = (id) => `<button class="linklike mono" data-flow="${esc(id)}">${esc(id)}</button>`;
  const recLink = (id) => (R[id] ? `<button class="linklike" data-rec="${esc(id)}">${esc(shortRec(id))}</button>` : esc(id));
  function shortRec(id) {
    const n = R[id].name.replace(/,\s*App\.\s*\d+[A-Z]?.*$/, "");
    return n.length > 70 ? n.slice(0, 68) + "…" : n;
  }
  function gapsHtml(ids) {
    if (!ids.length) return "";
    return "<h3>Open questions</h3><ul class=\"plain\">" + ids.map((g) => `<li><span class="pill ${G[g].status === "open" ? "not_stated" : ""}">${esc(G[g].status.replace("_", " "))}</span> ${esc(G[g].question)} <span class="note">Who could settle it: ${esc(G[g].who_could_settle)}.</span></li>`).join("") + "</ul>";
  }
  function flowRow(fid, dir) {
    const f = F[fid];
    const other = dir === "out" ? f.to_id : f.from_id;
    return `<li class="flowline"><span>${flowLink(fid)}</span><span>${dir === "out" ? "to" : "from"} ${nodeLink(other)}: ${esc(f.what_passes)} <span class="pill kind-${f.kind}">${esc(SHORT.kind[f.kind])}</span> <span class="pill ${f.stage}">${esc(SHORT.stage[f.stage])}</span></span></li>`;
  }
  function bindClicks(root) {
    root.querySelectorAll("[data-node]").forEach((b) => b.addEventListener("click", () => { showTab("map"); revealNode(b.dataset.node); }));
    root.querySelectorAll("[data-flow]").forEach((b) => b.addEventListener("click", () => { showTab("map"); revealFlow(b.dataset.flow); }));
    root.querySelectorAll("[data-rec]").forEach((b) => b.addEventListener("click", () => { showTab("map"); panelRecord(b.dataset.rec); }));
    root.querySelectorAll("[data-net]").forEach((b) => b.addEventListener("click", () => { showTab("nets"); openNet(b.dataset.net, b.dataset.coh || null, b.dataset.el || null); }));
    root.querySelectorAll("[data-toggle]").forEach((b) => b.addEventListener("click", () => toggleNode(b.dataset.toggle)));
  }
  function setPanel(html) { const p = $("panel"); p.innerHTML = html; p.scrollTop = 0; bindClicks(p); }

  function reviewHtml(typ, id) {
    const r = REV[typ + ":" + id];
    if (!r) return `<p class="review-note needs_evidence"><strong>Independent verification:</strong> not reviewed individually in this audit. The cited sources are references, not certification of operational use.</p>`;
    const status = {corroborated: "Public source corroborates the qualified claim", qualified: "Qualification needed", needs_evidence: "Operational claim not independently verified", model_inference: "Modelling inference, not observed system behavior"}[r.result] || r.result;
    return `<div class="review-note ${esc(r.result)}"><strong>Evidence review:</strong> ${esc(status)}. ${esc(r.finding)} ${r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">Official source</a>` : ""}<div class="note">Reviewed ${esc(r.reviewed_on)}. Scope: ${esc(r.scope)}.</div></div>`;
  }

  function panelOverview() {
    const sys = D.nodes.filter((n) => n.type === "system");
    const inUse = sys.filter((n) => n.status === "in_use" || n.status === "in_use_part").length;
    const planned = sys.filter((n) => n.status === "planned").length;
    const atlasRows = new Set(D.flows.filter((f) => f.atlas_row).map((f) => f.atlas_row)).size;
    setPanel(`
      <p class="eyebrow">Facts as of ${esc(D.as_of)}</p>
      <h2>One map, three levels</h2>
      <p>Level 0 shows the institutions and the parties outside government. Level 1 opens each institution to its systems and units. Level 2 opens the systems that have modules, such as BTMS and PhilGEPS. You can also open or close one box at a time by double-clicking it.</p>
      <p>A number on a line is the count of flows between two closed boxes. Click a box or a line to read about it here.</p>
      <p>Each line is a flow: something that passes from one body or system to another. Its colour tells what passes, its pattern tells how it passes.</p>
      <dl class="kv">
        <dt>Institutions</dt><dd>${D.nodes.filter((n) => n.level === "0").length}</dd>
        <dt>Systems</dt><dd>${sys.length}: ${inUse} in use, ${planned} planned, the rest described or not verified</dd>
        <dt>Flows</dt><dd>${D.flows.length}, from ${atlasRows} rows of the atlas register and ${D.flows.filter((f) => !f.atlas_row).length} new rows</dd>
        <dt>Process steps</dt><dd>${D.steps.length}, from ${Object.keys(SEQ).length} sequence diagrams of the atlas</dd>
        <dt>Records</dt><dd>${D.records.length}</dd>
        <dt>Open questions</dt><dd>${D.gaps.length}</dd>
      </dl>
      <h3>Where to start</h3>
      <ul class="plain">
        <li>${nodeLink("SYS-BTMS")}: the core of the planned IFMIS</li>
        <li>${flowLink("F032")}: the payment order that goes to the bank on paper</li>
        <li>${flowLink("F027")}: the same payment from BTMS through the clearing houses</li>
        <li><button class="linklike" data-net="CH-SPEND" data-coh="P">The spending chain as a Petri net, cohort P</button></li>
      </ul>
      <p class="note">Operational status is an evidence classification, not an agency-by-agency deployment certification. "Not stated" never means "absent". It means that the sources read do not say.</p>`);
  }

  function selectNode(id) {
    state.selected = id;
    if (cy) { cy.elements().unselect(); const el = cy.getElementById(id); if (el.length) { el.select(); highlight(el); } }
    const n = N[id];
    const out = D.flows.filter((f) => [f.from_id].includes(id) || leavesOf(id).includes(f.from_id) || ancestors(f.from_id).includes(id)).map((f) => f.flow_id);
    const inn = D.flows.filter((f) => ancestors(f.to_id).includes(id)).map((f) => f.flow_id);
    const via = D.flows.filter((f) => f.via_id && ancestors(f.via_id).includes(id)).map((f) => f.flow_id);
    const steps = D.steps.filter((s) => ancestors(s.who_node).includes(id) || (s.to_node && ancestors(s.to_node).includes(id)));
    const gaps = D.gaps.filter((g) => split(g.related).some((r) => r === id)).map((g) => g.gap_id);
    const kids = n.children.length ? `<h3>Inside</h3><ul class="plain">${n.children.map((k) => `<li>${nodeLink(k)} <span class="note">${esc(N[k].type)}${N[k].status ? ", " + esc(SHORT.status[N[k].status] || N[k].status) : ""}</span></li>`).join("")}</ul>` : "";
    const trans = D.transitions.filter((t) => t.node_id === id);
    const holders = D.holders.filter((h) => h.held_in === id);
    const toggle = n.children.length ? `<p><button class="btn" data-toggle="${esc(id)}">${state.expanded.has(id) ? "Close this box" : "Open this box"}</button></p>` : "";
    setPanel(`
      <p class="eyebrow">${esc(id)} · level ${esc(n.level)} · ${esc(n.type)}</p>
      <h2>${esc(n.full_name)}</h2>
      <div class="pills">${n.status ? `<span class="pill ${esc(n.status)}">${esc(SHORT.status[n.status] || n.status)}</span>` : ""}${n.scope === "adjacent" ? '<span class="pill">adjacent to PFM</span>' : ""}${n.since ? `<span class="pill">since ${esc(n.since)}</span>` : ""}</div>
      ${toggle}
      <p>${esc(n.description)}</p>
      ${reviewHtml("node", id)}
      <dl class="kv">
        ${n.parent_id ? `<dt>Part of</dt><dd>${nodeLink(n.parent_id)}</dd>` : ""}
        ${n.owner ? `<dt>Owner</dt><dd>${esc(n.owner)}</dd>` : ""}
        ${n.users ? `<dt>Enters the data</dt><dd>${esc(n.users)}</dd>` : ""}
        ${n.recipients ? `<dt>Reads the data</dt><dd>${esc(n.recipients)}</dd>` : ""}
        ${evLine(n.ev, n.basis)}
        ${n.atlas_ref ? `<dt>In the atlas</dt><dd>${esc(n.atlas_ref)}</dd>` : ""}
      </dl>
      ${n.note ? `<p class="callout">${esc(n.note)}</p>` : ""}
      ${kids}
      ${out.length ? `<h3>Flows out (${out.length})</h3><ul class="plain">${out.map((f) => flowRow(f, "out")).join("")}</ul>` : ""}
      ${inn.length ? `<h3>Flows in (${inn.length})</h3><ul class="plain">${inn.map((f) => flowRow(f, "in")).join("")}</ul>` : ""}
      ${via.length ? `<h3>Flows that pass through it</h3><ul class="plain">${via.map((f) => `<li class="flowline"><span>${flowLink(f)}</span><span>${esc(F[f].what_passes)}</span></li>`).join("")}</ul>` : ""}
      ${holders.length ? `<h3>Records held here in the nets</h3><ul class="plain">${holders.map((h) => `<li><button class="linklike" data-net="${esc(chainOfPlace(h.place_id))}" data-coh="${h.cohort === "all" ? "P" : esc(h.cohort)}" data-el="${esc(h.place_id)}">${esc(PL[h.place_id].name)}</button> <span class="note">cohort ${esc(h.cohort)}</span></li>`).join("")}</ul>` : ""}
      ${trans.length ? `<h3>Acts in the process nets</h3><ul class="plain">${trans.map((t) => `<li><button class="linklike" data-net="${esc(t.chain_id)}" data-coh="${esc(cohortsOf(t.cohorts)[0])}" data-el="${esc(t.transition_id)}">${esc(t.transition_id)} ${esc(t.name)}</button></li>`).join("")}</ul>` : ""}
      ${steps.length ? `<h3>Process steps of the atlas (${steps.length})</h3><ul class="plain">${steps.slice(0, 40).map((s) => `<li><span class="mono">${esc(s.step_id)}</span> ${esc(N[s.who_node].name)}${s.own_action === "yes" ? "" : " to " + esc(N[s.to_node].name)}: ${esc(s.text)}</li>`).join("")}${steps.length > 40 ? `<li class="note">and ${steps.length - 40} more</li>` : ""}</ul>` : ""}
      ${gapsHtml(gaps)}`);
  }
  function chainOfPlace(pid) {
    const t = D.transitions.find((t) => D.nets.some((n) => n.chain === t.chain_id && n.arcs.some((a) => a.p === pid && a.t === t.transition_id)));
    return t ? t.chain_id : "CH-SPEND";
  }

  function panelFlow(fid) {
    const f = F[fid];
    const L = edgeLook(f);
    const steps = f.steps.map((s) => ST[s]);
    const places = f.places.map((p) => PL[p]);
    const recs = split(f.payload);
    setPanel(`
      <p class="eyebrow">${esc(fid)}${f.atlas_row ? " · row " + esc(f.atlas_row) + " of the atlas register (Reference B)" : " · new in this repository"}</p>
      <h2>${esc(f.what_passes)}</h2>
      <p>${nodeLink(f.from_id)} ${f.via_id ? "through " + nodeLink(f.via_id) + " " : ""}to ${nodeLink(f.to_id)}</p>
      <div class="pills"><span class="pill kind-${f.kind}">${esc(SHORT.kind[f.kind])}</span><span class="pill ${f.stage}">${esc(SHORT.stage[f.stage])}</span><span class="pill">${esc(SHORT.domain[f.domain])}</span><span class="pill">cohorts: ${esc(f.cohorts === "all" ? "all" : f.cohorts.replace(/;/g, ", "))}</span></div>
      <dl class="kv">
        <dt>Who moves it</dt><dd>${esc(SHORT.agent[f.agent])}<br><span class="note">${esc(V["flows.agent"][f.agent])}</span></dd>
        <dt>Medium</dt><dd>${esc(SHORT.medium[f.medium])}<br><span class="note">${esc(V["flows.medium"][f.medium])}</span></dd>
        ${f.atlas_carrier ? `<dt>Carrier in the atlas</dt><dd>${esc(f.atlas_carrier)}</dd>` : ""}
        ${f.timing ? `<dt>Timing</dt><dd>${esc(f.timing)}</dd>` : ""}
        ${f.standard ? `<dt>Message standard</dt><dd>${esc(f.standard)}</dd>` : ""}
        <dt>Check of both sides</dt><dd>${esc(f.check)}</dd>
        ${evLine(f.ev, f.basis)}
      </dl>
      ${reviewHtml("flow", fid)}
      ${f.note ? `<p class="callout">${esc(f.note)}</p>` : ""}
      ${recs.length ? `<h3>Records that pass</h3><ul class="plain">${recs.map((r) => `<li>${recLink(r)} <span class="note">${esc(R[r].kind)}${R[r].form_ref ? ", " + esc(R[r].form_ref) : ""}</span></li>`).join("")}</ul>` : ""}
      ${places.length ? `<h3>Places in the process nets</h3><ul class="plain">${places.map((p) => `<li><button class="linklike" data-net="${esc(chainOfPlace(p.place_id))}" data-coh="${esc(cohortsOf(p.cohorts)[0])}" data-el="${esc(p.place_id)}">${esc(p.place_id)}: ${esc(p.name)}</button></li>`).join("")}</ul>` : ""}
      ${steps.length ? `<h3>Steps of the atlas that show it</h3><ul class="plain">${steps.map((s) => `<li><span class="mono">${esc(s.step_id)}</span> ${esc(s.text)}</li>`).join("")}</ul>` : ""}
      ${gapsHtml(split(f.gaps))}
      <p class="note">Line in the map: ${esc(L.dash)} for the medium, colour for the kind${f.stage === "planned" ? ", hollow arrow for a plan" : ""}.</p>`);
  }
  function panelAgg(data) {
    const fl = data.flows;
    setPanel(`
      <p class="eyebrow">${fl.length} flow${fl.length > 1 ? "s" : ""} between two boxes</p>
      <h2>${esc(N[data.source].name)} to ${esc(N[data.target].name)}</h2>
      <p>The boxes are closed, so the flows between their contents are drawn as one line. Open a box to see each flow on its own.</p>
      <ul class="plain">${fl.map((f) => `<li class="flowline"><span>${flowLink(f)}</span><span>${nodeLink(F[f].from_id)} to ${nodeLink(F[f].to_id)}: ${esc(F[f].what_passes)} <span class="pill kind-${F[f].kind}">${esc(SHORT.kind[F[f].kind])}</span> <span class="pill ${F[f].stage}">${esc(SHORT.stage[F[f].stage])}</span></span></li>`).join("")}</ul>
      <p><button class="btn" data-toggle="${esc(N[data.source].children.length && !state.expanded.has(data.source) ? data.source : data.target)}">Open a box</button></p>`);
  }
  function panelSteps(data) {
    setPanel(`
      <p class="eyebrow">${data.steps.length} process step${data.steps.length > 1 ? "s" : ""} without a flow in the register</p>
      <h2>${esc(N[data.source].name)} to ${esc(N[data.target].name)}</h2>
      <p>These steps come from the sequence diagrams of the atlas. They pass a document or a request, but no row of the register of flows describes them as a flow between systems.</p>
      <ul class="plain">${data.steps.map((s) => `<li><span class="mono">${esc(s)}</span> ${esc(ST[s].text)} <span class="note">[${esc(ST[s].basis)}]</span></li>`).join("")}</ul>`);
  }
  function panelRecord(rid) {
    const r = R[rid];
    const fl = D.flows.filter((f) => split(f.payload).includes(rid));
    const pl = D.places.filter((p) => split(p.records).includes(rid));
    const links = D.links.filter((l) => l.from_record === rid || l.to_record === rid);
    setPanel(`
      <p class="eyebrow">${esc(rid)} · ${esc(r.kind)}</p>
      <h2>${esc(r.name)}</h2>
      <p>${esc(r.purpose)}</p>
      <dl class="kv">
        <dt>Issued by</dt><dd>${esc(r.issuer)}${r.issuer_node ? " (" + nodeLink(r.issuer_node) + ")" : ""}</dd>
        <dt>Identified by</dt><dd>${esc(r.identified_by)}</dd>
        ${r.form_ref ? `<dt>Form</dt><dd>${esc(r.form_ref)}</dd>` : ""}
        <dt>Basis</dt><dd>${esc(r.basis)}</dd>
      </dl>
      ${r.fields.length ? `<h3>Fields (diagram 17c of the atlas)</h3><div class="tablewrap"><table class="fields"><thead><tr><th>Field</th><th>Type</th><th>Key</th><th>Note</th></tr></thead><tbody>${r.fields.map((f) => `<tr><td class="mono">${esc(f.field)}</td><td>${esc(f.type)}</td><td>${esc(f.key)}${f.references ? " to " + recLink(f.references) : ""}</td><td>${esc(f.note)}${f.basis === "GK" ? ' <span class="pill gk">general knowledge</span>' : ""}</td></tr>`).join("")}</tbody></table></div>` : ""}
      ${links.length ? `<h3>Links to other records</h3><ul class="plain">${links.map((l) => `<li>${recLink(l.from_record)} ${esc(l.relation)} ${recLink(l.to_record)} <span class="note">${l.key ? "key: " + esc(l.key) : "key not stated"}${l.basis === "GK" ? '</span> <span class="pill gk">general knowledge</span>' : "</span>"}</li>`).join("")}</ul>` : ""}
      ${fl.length ? `<h3>Flows that carry it (${fl.length})</h3><ul class="plain">${fl.map((f) => `<li class="flowline"><span>${flowLink(f.flow_id)}</span><span>${nodeLink(f.from_id)} to ${nodeLink(f.to_id)}</span></li>`).join("")}</ul>` : ""}
      ${pl.length ? `<h3>Places in the process nets</h3><ul class="plain">${pl.map((p) => `<li><button class="linklike" data-net="${esc(chainOfPlace(p.place_id))}" data-coh="${esc(cohortsOf(p.cohorts)[0])}" data-el="${esc(p.place_id)}">${esc(p.place_id)}: ${esc(p.name)}</button></li>`).join("")}</ul>` : ""}`);
  }
  function selectEdge(edge) {
    const d = edge.data();
    state.selected = edge.id();
    highlight(edge);
    if (d.etype === "flow") panelFlow(d.flow);
    else if (d.etype === "agg") panelAgg(d);
    else panelSteps(d);
  }

  // --------------------------------------------------------------- filters, legend, search
  function buildFilters() {
    const box = $("filterbox");
    const groups = [["kind", "What passes"], ["stage", "Stage of use"], ["agent", "Who moves it"], ["medium", "Medium"], ["domain", "Part of PFM"]];
    box.innerHTML = groups.map(([k, title]) => `<fieldset><legend>${title}</legend>${Object.entries(SHORT[k]).map(([v, lab]) => `<label title="${esc((V["flows." + k] || {})[v] || "")}"><input type="checkbox" id="f-${k}-${v}" data-k="${k}" data-v="${v}" checked> ${esc(lab)}</label>`).join("")}</fieldset>`).join("")
      + `<fieldset><legend>Sources</legend><label><input type="checkbox" id="f-gk" checked> Flows whose best source is general knowledge</label></fieldset>`
      + `<div><button class="btn ghost" id="f-reset" type="button">Show all flows</button></div>`;
    box.querySelectorAll("input[data-k]").forEach((i) => i.addEventListener("change", () => { const s = state[i.dataset.k]; if (i.checked) s.add(i.dataset.v); else s.delete(i.dataset.v); renderMap(); }));
    $("f-gk").addEventListener("change", (e) => { state.gkOnly = e.target.checked; renderMap(); });
    $("f-reset").addEventListener("click", () => { resetFilters(); state.cohort = "all"; $("cohort").value = "all"; renderMap(); });
  }
  function resetFilters() {
    ["kind", "stage", "agent", "medium", "domain"].forEach((k) => { state[k] = new Set(Object.keys(SHORT[k])); });
    state.gkOnly = true;
    $("filterbox").querySelectorAll("input[type=checkbox]").forEach((i) => { i.checked = true; });
  }
  function svgLine(color, dash, width, hollow) {
    const da = dash === "dotted" ? "2 4" : dash === "dashed" ? "7 4" : dash === "steps" ? "2 5" : "";
    return `<svg width="38" height="10" aria-hidden="true"><line x1="1" y1="5" x2="30" y2="5" stroke="${color}" stroke-width="${width}" ${da ? `stroke-dasharray="${da}"` : ""}/><path d="M30 1 L37 5 L30 9 Z" fill="${hollow ? "none" : color}" stroke="${color}"/></svg>`;
  }
  function buildLegend() {
    const K = KIND();
    $("legend").innerHTML = [
      ["Authority", svgLine(K.authority, "solid", 2)], ["Paper", svgLine(T["--ink"], "dotted", 2)],
      ["Document", svgLine(K.document, "solid", 2)], ["Entered or downloaded by a person", svgLine(T["--ink"], "dashed", 2)],
      ["Data", svgLine(K.data, "solid", 2)], ["Program to program", svgLine(T["--ink"], "solid", 3.2)],
      ["Money", svgLine(K.money, "solid", 2.6)], ["Planned", svgLine(T["--ink"], "solid", 2, true)],
    ].map(([t, s]) => `<span class="k">${s}${esc(t)}</span>`).join("") + (state.showSteps ? `<span class="k">${svgLine(T["--muted"], "steps", 1.4)}Process step</span>` : "");
    buildNetLegend(netState.id.startsWith("SEQ:"));
  }
  function buildNetLegend(isSeq) {
    const box = (fill, stroke, sw, dash) => `<svg width="22" height="14" aria-hidden="true"><rect x="1" y="2" width="20" height="10" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" ${dash ? `stroke-dasharray="${dash}"` : ""}/></svg>`;
    const ell = (fill, stroke, sw, dash) => `<svg width="22" height="14" aria-hidden="true"><ellipse cx="11" cy="7" rx="10" ry="6" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" ${dash ? `stroke-dasharray="${dash}"` : ""}/></svg>`;
    if (isSeq) {
      $("netlegend").innerHTML = [
        [`<svg width="22" height="14" aria-hidden="true"><circle cx="11" cy="7" r="6" fill="${T["--ink"]}"/></svg>`, "Start, with its token"],
        [`<svg width="22" height="14" aria-hidden="true"><circle cx="11" cy="7" r="6" fill="${T["--surface"]}" stroke="${T["--ink"]}"/></svg>`, "Place between two steps"],
        [box(T["--surface"], T["--ink"], 1.6), "Step of the diagram"],
        [`<svg width="22" height="14" aria-hidden="true"><rect x="7" y="3" width="8" height="8" fill="${T["--ink"]}"/></svg>`, "Silent transition"],
      ].map(([s, t]) => `<span class="k">${s}${esc(t)}</span>`).join("");
      return;
    }
    const LS = LINESOFT(), LL = LINE();
    $("netlegend").innerHTML = Object.keys(LL).map((k) => `<span class="k">${ell(LS[k], LL[k], 1)}${esc({ authority: "Authority", claim: "Claim", cash: "Cash", records: "Records" }[k])}</span>`).join("")
      + `<span class="k">${box(T["--surface"], T["--ink"], 1.6)}Act by a person</span>`
      + `<span class="k">${box(T["--raise"], T["--ink"], 1.6)}Act by software</span>`
      + `<span class="k">${ell("none", T["--ink"], 1, "3 2")}Record on its way</span>`
      + `<span class="k">${ell("none", T["--ink"], 3)}Balance</span>`;
  }
  function buildSearch() {
    const opts = D.nodes.map((n) => n.name).concat(D.flows.map((f) => f.flow_id)).concat(D.records.map((r) => shortRec(r.record_id)));
    $("qlist").innerHTML = [...new Set(opts)].map((o) => `<option value="${esc(o)}"></option>`).join("");
    $("q").addEventListener("change", (e) => runSearch(e.target.value));
    $("q").addEventListener("keydown", (e) => { if (e.key === "Enter") runSearch(e.target.value); });
  }
  function runSearch(v) {
    const q = v.trim().toLowerCase();
    if (!q) return;
    const flow = D.flows.find((f) => f.flow_id.toLowerCase() === q);
    if (flow) { revealFlow(flow.flow_id); return; }
    const node = D.nodes.find((n) => n.name.toLowerCase() === q) || D.nodes.find((n) => n.node_id.toLowerCase() === q)
      || D.nodes.find((n) => (n.name + " " + n.full_name).toLowerCase().includes(q));
    if (node) { revealNode(node.node_id); return; }
    const rec = D.records.find((r) => shortRec(r.record_id).toLowerCase() === q) || D.records.find((r) => r.name.toLowerCase().includes(q));
    if (rec) { panelRecord(rec.record_id); return; }
    setPanel(`<h2>Nothing found</h2><p>No box, flow or record matches "${esc(v)}". Try a system name such as BTMS, a flow number such as F032, or a form such as LDDAP.</p>`);
  }

  // --------------------------------------------------------------- process nets
  let cyn = null;
  const netState = { id: "CH-SPEND", cohort: "P" };
  function netStyle() {
    return [
      { selector: "node", style: { "font-family": T["--font-body"], "font-size": 9, color: T["--ink"], label: "data(label)", "text-wrap": "wrap", "text-max-width": "data(tw)", "text-valign": "center", "text-halign": "center", width: "data(w)", height: "data(h)" } },
      { selector: "node[k = 'place']", style: { shape: "ellipse", "background-color": "data(fill)", "border-color": "data(stroke)", "border-width": 1.2 } },
      { selector: "node[pk = 'channel']", style: { "border-style": "dashed" } },
      { selector: "node[pk = 'balance']", style: { "border-style": "double", "border-width": 4 } },
      { selector: "node[pk = 'clock']", style: { "border-style": "dotted", "border-width": 2 } },
      { selector: "node[k = 'trans']", style: { shape: "rectangle", "background-color": "data(fill)", "border-color": T["--ink"], "border-width": 1.8 } },
      { selector: "node[k = 'silent']", style: { shape: "rectangle", "background-color": T["--ink"], "border-width": 0, label: "" } },
      { selector: "node[k = 'splace']", style: { shape: "ellipse", "background-color": T["--surface"], "border-color": T["--ink"], "border-width": 1.2, "font-size": 8, "text-valign": "bottom", "text-margin-y": 3 } },
      { selector: "node[init = 1]", style: { "background-color": T["--ink"] } },
      { selector: "edge", style: { "curve-style": "bezier", width: 1.2, "line-color": T["--muted"], "target-arrow-color": T["--muted"], "target-arrow-shape": "triangle", "arrow-scale": 0.8, label: "data(label)", "font-size": 8, color: T["--muted"], "text-background-color": T["--bg"], "text-background-opacity": 0.85 } },
      { selector: "edge[d = 'read']", style: { "line-style": "dotted", "target-arrow-shape": "none", width: 1.4 } },
      { selector: ":selected", style: { "border-color": T["--accent"], "border-width": 3, "line-color": T["--accent"], "target-arrow-color": T["--accent"] } },
      { selector: ".hl", style: { "border-color": T["--accent"], "border-width": 3 } },
    ];
  }
  function bindingOf(tid, coh) {
    const rows = D.bindings.filter((b) => b.transition_id === tid);
    return rows.find((b) => b.cohort === coh) || rows.find((b) => b.cohort === "all") || null;
  }
  function holderOf(pid, coh) {
    const rows = D.holders.filter((h) => h.place_id === pid);
    return rows.find((h) => h.cohort === coh) || rows.find((h) => h.cohort === "all") || null;
  }
  function netElements(net, isSeq) {
    const els = [];
    if (isSeq) {
      net.places.forEach((p) => els.push({ data: { id: p.id, k: "splace", label: p.name, w: 18, h: 18, tw: 60, init: p.id === net.start ? 1 : 0 }, position: { x: p.x, y: p.y } }));
      net.transitions.forEach((t) => els.push({ data: { id: t.id, k: t.silent ? "silent" : "trans", label: t.silent ? "" : t.name, w: t.silent ? 12 : Math.max(t.w, 60), h: t.silent ? 12 : Math.max(t.h, 26), tw: Math.max(t.w - 10, 50), fill: T["--surface"] }, position: { x: t.x, y: t.y } }));
      net.arcs.forEach((a, i) => els.push({ data: { id: "e" + i, source: a.s, target: a.t, label: "" } }));
      return els;
    }
    const LS = LINESOFT(), LL = LINE();
    net.places.forEach((p) => {
      const P = PL[p.id];
      const lab = (P.flow_id ? P.flow_id + ": " : "") + P.name + (P.initial ? " ●" : "");
      els.push({ data: { id: p.id, k: "place", pk: P.kind, label: lab, w: p.w, h: p.h, tw: p.w - 16, fill: LS[P.line], stroke: LL[P.line] }, position: { x: p.x, y: p.y } });
    });
    net.transitions.forEach((t) => {
      const b = bindingOf(t.id, net.cohort);
      const fill = b && b.controller_kind === "software" ? T["--raise"] : T["--surface"];
      els.push({ data: { id: t.id, k: "trans", label: t.id + "\n" + TR[t.id].name, w: t.w, h: t.h, tw: t.w - 10, fill }, position: { x: t.x, y: t.y } });
    });
    net.arcs.forEach((a, i) => {
      const src = a.d === "out" ? a.t : a.p, tgt = a.d === "out" ? a.p : a.t;
      els.push({ data: { id: "e" + i, source: src, target: tgt, d: a.d, label: a.w === "amount" ? "amount" : a.d === "read" ? "read" : "" } });
    });
    return els;
  }
  function buildNetSelect() {
    const sel = $("netsel");
    const curated = D.chains_meta.map((c) => `<option value="${esc(c.chain_id)}">${esc(c.name)}</option>`).join("") + '<option value="CH-ALL">All chains together</option>';
    const seqs = D.sequences.map((s) => {
      const t = s.title.startsWith(s.id) ? s.title : s.id + " " + s.title;
      return `<option value="SEQ:${esc(s.id)}">${esc(t.length > 84 ? t.slice(0, 82) + "…" : t)}</option>`;
    }).join("");
    sel.innerHTML = `<optgroup label="Curated chains, by cohort">${curated}</optgroup><optgroup label="Workflow nets of the atlas sequence diagrams">${seqs}</optgroup>`;
    sel.addEventListener("change", () => openNet(sel.value, null, null));
    document.querySelectorAll("#netcoh button").forEach((b) => b.addEventListener("click", () => openNet(netState.id, b.dataset.c, null)));
  }
  function openNet(id, coh, focusId) {
    netState.id = id;
    if (coh) netState.cohort = coh;
    $("netsel").value = id;
    const isSeq = id.startsWith("SEQ:");
    document.querySelectorAll("#netcoh button").forEach((b) => { b.disabled = isSeq; b.setAttribute("aria-pressed", String(!isSeq && b.dataset.c === netState.cohort)); });
    let net = null;
    if (isSeq) net = SEQ[id.slice(4)];
    else {
      net = NETS[id + "-" + netState.cohort];
      if (!net) { const any = ["P", "E", "B"].find((c) => NETS[id + "-" + c]); netState.cohort = any; net = NETS[id + "-" + any]; document.querySelectorAll("#netcoh button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.c === any))); }
    }
    if (!cyn) {
      cyn = cytoscape({ container: $("cynet"), elements: [], style: netStyle(), minZoom: 0.05, maxZoom: 3, boxSelectionEnabled: false });
      cyn.on("tap", "node", (e) => netPanel(e.target.id()));
      cyn.on("tap", (e) => { if (e.target === cyn) netPanel(null); });
    }
    buildNetLegend(isSeq);
    cyn.batch(() => { cyn.elements().remove(); cyn.add(netElements(net, isSeq)); });
    cyn.layout({ name: "preset", fit: true, padding: 30 }).run();
    let big = false;
    if (cyn.zoom() < 0.6) {
      // The whole net is too small to read: start at its top, at a size that can be read.
      big = true;
      const bb = cyn.elements().boundingBox();
      const z = 0.9;
      cyn.viewport({ zoom: z, pan: { x: cyn.width() / 2 - z * (bb.x1 + bb.w / 2), y: 24 - z * bb.y1 } });
    }
    const tail = big ? " The view starts at the top of the net; the square button shows all of it." : "";
    if (isSeq) {
      const s = net.sound;
      $("netinfo").textContent = `${net.transitions.filter((t) => !t.silent).length} steps, ${net.transitions.filter((t) => t.silent).length} silent transitions. Sound: ${s.sound ? "yes" : "no"} (${s.states} reachable markings).` + tail;
    } else {
      $("netinfo").textContent = `${net.transitions.length} transitions, ${net.places.length} places in cohort ${net.cohort}. Places with no input: ${net.sources.length}; with no output: ${net.sinks.length}.` + tail;
    }
    if (focusId) { const el = cyn.getElementById(focusId); if (el.length) { el.select(); focusOn(cyn, el, 120, 1.0, true); netPanel(focusId); return; } }
    netPanel(null);
  }
  function netPanelSet(html) { const p = $("netpanel"); p.innerHTML = html; p.scrollTop = 0; bindClicks(p); }
  function netPanel(elId) {
    const id = netState.id;
    const isSeq = id.startsWith("SEQ:");
    if (!elId) {
      if (isSeq) {
        const s = SEQ[id.slice(4)];
        netPanelSet(`<p class="eyebrow">Atlas diagram ${esc(s.id)}</p><h2>${esc(s.title)}</h2>
          <p>This workflow net is made from the sequence diagram of the atlas. Each message or own action is a transition, in the order of the diagram. A choice of the diagram (alt) is an exclusive choice, an optional block (opt) is a choice with a silent skip, a parallel block (par) is a split and a join, and a loop can repeat or exit. Small black squares are silent transitions.</p>
          <dl class="kv"><dt>Sound</dt><dd>${s.sound.sound ? "Yes" : "No"}: every reachable marking can reach the end, the end marking holds one token only, and every transition can fire.</dd><dt>Reachable markings</dt><dd>${s.sound.states}</dd></dl>`);
      } else {
        const c = id === "CH-ALL" ? { name: "All chains together", question: "How do the chains connect through the places they share (the Treasury Single Account, the allotment, the obligation, the books)?", atlas_ref: "" } : CH[id];
        const ucs = D.use_cases.filter((u) => u.chain_id === id);
        netPanelSet(`<p class="eyebrow">${esc(id)} · cohort ${esc(netState.cohort)}: ${esc(CO[netState.cohort].name)}</p><h2>${esc(c.name)}</h2>
          <p>${esc(c.question)}</p>
          <p class="note">${esc(CO[netState.cohort].description)}</p>
          ${c.atlas_ref ? `<p class="note">Built from: ${esc(c.atlas_ref)}.</p>` : ""}
          <p>A box is an act of a role. An ellipse is a place: a state, a balance (double border), a record on its way between bodies (dashed border, named after its flow), or a moment of the calendar (dotted). A dotted line marked "read" is an arc that needs the token and leaves it. Grey boxes are acts done by software in this cohort.</p>
          ${ucs.length ? `<h3>ICONIX use cases of this chain</h3><ul class="plain">${ucs.map((u) => `<li><span class="mono">${esc(u.use_case_id)}</span> ${esc(u.name)}: ${esc(u.goal)}</li>`).join("")}</ul><p class="note">The robustness and sequence diagrams of each use case and cohort are in the folder iconix/ of the repository.</p>` : ""}`);
      }
      return;
    }
    if (isSeq) {
      const s = SEQ[id.slice(4)];
      const t = s.transitions.find((x) => x.id === elId);
      if (!t) { netPanel(null); return; }
      if (t.silent) { netPanelSet(`<h2>Silent transition</h2><p>${esc(t.name)}</p><p class="note">It moves the token without an act of a person or a system. It stands for the structure of the diagram: a choice, a skip, a split, a join or a loop.</p>`); return; }
      const st = ST[t.step];
      netPanelSet(`<p class="eyebrow">Step ${esc(t.step)}</p><h2>${esc(st.text)}</h2>
        <dl class="kv"><dt>Acts</dt><dd>${nodeLink(st.who_node)}${st.who_role ? " (" + esc(RO[st.who_role].name) + ")" : ""}</dd>${st.own_action === "yes" ? "" : `<dt>Toward</dt><dd>${nodeLink(st.to_node)}</dd>`}
        ${st.block ? `<dt>Block</dt><dd>${esc(st.block)}</dd>` : ""}<dt>Basis</dt><dd>${esc(st.basis)}</dd>
        ${split(st.flows).length ? `<dt>Flows</dt><dd>${split(st.flows).map(flowLink).join(" ")}</dd>` : ""}</dl>`);
      return;
    }
    const coh = netState.cohort;
    if (TR[elId]) {
      const t = TR[elId];
      const b = bindingOf(elId, coh);
      const rules = split(t.rules).map((r) => RU[r]);
      const ucs = D.use_cases.filter((u) => split(u.transitions).includes(elId));
      netPanelSet(`<p class="eyebrow">${esc(elId)} · ${esc(CH[t.chain_id].name)}</p><h2>${esc(t.name)}</h2>
        <dl class="kv"><dt>Role</dt><dd>${esc(RO[t.role_id].name)}</dd><dt>Where</dt><dd>${nodeLink(t.node_id)}</dd><dt>Cohorts</dt><dd>${esc(t.cohorts === "all" ? "all" : t.cohorts.replace(/;/g, ", "))}</dd><dt>Basis</dt><dd>${esc(t.basis)}</dd></dl>
        ${t.note ? `<p class="callout">${esc(t.note)}</p>` : ""}
        ${b ? `<h3>In cohort ${esc(coh)}</h3><dl class="kv"><dt>Boundary</dt><dd>${esc(b.boundary)}${b.boundary_node ? " (" + nodeLink(b.boundary_node) + ")" : ""}</dd><dt>Control</dt><dd>${esc(b.controller)} <span class="pill">${esc(b.controller_kind.replace("_", " "))}</span></dd>${b.writes_in ? `<dt>Writes in</dt><dd>${split(b.writes_in).map(nodeLink).join(", ")}</dd>` : ""}<dt>Basis</dt><dd>${esc(b.basis)}</dd></dl>${b.note ? `<p class="note">${esc(b.note)}</p>` : ""}` : ""}
        ${rules.length ? `<h3>Rules checked</h3><ul class="plain">${rules.map((r) => `<li><span class="mono">${esc(r.rule_id)}</span> ${esc(r.statement)}. <span class="note">In cohort ${esc(coh)}: ${esc(r["enforced_in_" + coh])}.</span></li>`).join("")}</ul>` : ""}
        ${ucs.length ? `<h3>ICONIX use case</h3><p>${ucs.map((u) => `<span class="mono">${esc(u.use_case_id)}</span> ${esc(u.name)}`).join("; ")}</p>` : ""}
        ${split(t.steps).length ? `<h3>Steps of the atlas</h3><ul class="plain">${split(t.steps).map((s) => `<li><span class="mono">${esc(s)}</span> ${esc(ST[s].text)}</li>`).join("")}</ul>` : ""}`);
      return;
    }
    if (PL[elId]) {
      const p = PL[elId];
      const h = holderOf(elId, coh);
      netPanelSet(`<p class="eyebrow">${esc(elId)} · ${esc(p.kind)} · line of ${esc(p.line)}</p><h2>${esc(p.name)}</h2>
        <dl class="kv">${h ? `<dt>Held in (cohort ${esc(coh)})</dt><dd>${nodeLink(h.held_in)}${h.note ? `<br><span class="note">${esc(h.note)}</span>` : ""}</dd>` : ""}
        ${p.flow_id ? `<dt>Flow</dt><dd>${flowLink(p.flow_id)} ${esc(F[p.flow_id].what_passes)}</dd>` : ""}
        ${split(p.records).length ? `<dt>Records</dt><dd>${split(p.records).map(recLink).join("; ")}</dd>` : ""}
        <dt>Initial tokens</dt><dd>${esc(p.initial || "none")}</dd><dt>Basis</dt><dd>${esc(p.basis)}</dd></dl>
        ${p.kind === "balance" ? '<p class="note">A balance holds an amount that many cases share. In a place/transition net its tokens stand for units of money; in a coloured net they would carry the amount, the UACS code and the fund cluster.</p>' : ""}`);
    }
  }

  // --------------------------------------------------------------- lists
  function buildLists() {
    const pillStage = (s) => `<span class="pill ${s}">${esc(SHORT.stage[s])}</span>`;
    const flowsRows = D.flows.map((f) => `<tr data-flow="${esc(f.flow_id)}"><td class="id">${esc(f.flow_id)}</td><td>${esc(N[f.from_id].name)}</td><td>${f.via_id ? esc(N[f.via_id].name) : ""}</td><td>${esc(N[f.to_id].name)}</td><td>${esc(f.what_passes)}</td><td>${esc(SHORT.kind[f.kind])}</td><td>${esc(SHORT.agent[f.agent])}</td><td>${esc(SHORT.medium[f.medium])}</td><td>${pillStage(f.stage)}</td><td>${esc(f.cohorts)}</td><td class="id">${esc(f.ev.codes.join(", "))}</td></tr>`).join("");
    const sys = D.nodes.filter((n) => ["system", "account", "network", "standard", "website"].includes(n.type));
    const sysRows = sys.map((n) => `<tr data-node="${esc(n.node_id)}"><td class="id">${esc(n.node_id)}</td><td>${esc(n.name)}</td><td>${esc(N[n.parent_id].name)}</td><td>${n.status ? `<span class="pill ${esc(n.status)}">${esc(SHORT.status[n.status] || n.status)}</span>` : ""}</td><td>${esc(n.users)}</td><td>${esc(n.recipients)}</td><td class="id">${esc(n.ev.codes.join(", "))}</td></tr>`).join("");
    const srcRows = D.sources.map((s) => `<tr><td class="id">${esc(s.code)}</td><td>${esc(SHORT.ev[s.type] || s.type)}</td><td>${s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a>` : esc(s.title)}</td><td>${esc(s.how_read)}</td></tr>`).join("");
    const gaps = D.gaps.map((g) => `<div class="gapcard"><div class="pills"><span class="pill ${g.status === "open" ? "not_stated" : ""}">${esc(g.status.replace("_", " "))}</span><span class="pill mono">${esc(g.gap_id)}</span></div><div class="q">${esc(g.question)}</div><div>${esc(g.why_it_matters)}</div><div class="note">Who could settle it: ${esc(g.who_could_settle)}. What would settle it: ${esc(g.what_would_settle)}. ${esc(g.atlas_ref)}.</div><div class="pills">${split(g.related).map((r) => N[r] ? `<button class="linklike" data-node="${esc(r)}">${esc(N[r].name)}</button>` : F[r] ? flowLink(r) : R[r] ? recLink(r) : esc(r)).join(" ")}</div></div>`).join("");
    $("lists").innerHTML = `
      <section><h2>Flows (${D.flows.length})</h2><div class="tablewrap"><table class="grid"><thead><tr><th>ID</th><th>From</th><th>Through</th><th>To</th><th>What passes</th><th>Kind</th><th>Who moves it</th><th>Medium</th><th>Stage</th><th>Cohorts</th><th>Sources</th></tr></thead><tbody>${flowsRows}</tbody></table></div></section>
      <section><h2>Systems, accounts and standards (${sys.length})</h2><div class="tablewrap"><table class="grid"><thead><tr><th>ID</th><th>Name</th><th>Institution</th><th>Status</th><th>Enters the data</th><th>Reads the data</th><th>Sources</th></tr></thead><tbody>${sysRows}</tbody></table></div></section>
      <section><h2>Open questions (${D.gaps.length})</h2><div class="gapcards">${gaps}</div></section>
      <section><h2>Sources (${D.sources.length})</h2><div class="tablewrap"><table class="grid"><thead><tr><th>Code</th><th>Kind</th><th>Source</th><th>How it was read</th></tr></thead><tbody>${srcRows}</tbody></table></div></section>`;
    $("lists").querySelectorAll("tr[data-flow]").forEach((tr) => tr.addEventListener("click", () => { showTab("map"); revealFlow(tr.dataset.flow); }));
    $("lists").querySelectorAll("tr[data-node]").forEach((tr) => tr.addEventListener("click", () => { showTab("map"); revealNode(tr.dataset.node); }));
    bindClicks($("lists"));
  }

  function buildAbout() {
    const coh = D.cohorts.map((c) => `<tr><th>${esc(c.cohort_id)}</th><td><strong>${esc(c.name)}</strong>. ${esc(c.description)} <span class="note">${esc(c.note)}</span></td></tr>`).join("");
    $("about").innerHTML = `<div class="col">
      <h2>What this map is</h2>
      <p>A map of the information systems of Philippine public financial management, and of what passes between them: data, documents, authorities and money. It was built from the Philippine PFM Atlas (its register of interfaces, its sequence diagrams and its forms) and from a few newer public sources. Every box and every line carries the sources it rests on.</p>
      <h2>Three levels in one map</h2>
      <p>Level 0 has the institutions and the parties outside government. Level 1 has the systems, accounts and units inside each institution. Level 2 has the modules of the systems that have them. You can choose a level for the whole map, or open and close one box at a time with a double-click.</p>
      <p>Level 0 alone is drawn in a small layout, so that all of it can be read on one screen. As soon as one box is open, the full layout is used. In the full layout every box keeps its place: a closed box takes the space that its contents take when it is open, so opening or closing a box does not move the other boxes. In both layouts the institutions stand in the same zones: authority and budget on the left, the spending agency in the middle, banks, Treasury and revenue on the right, parties outside government at the far right, and oversight and the public on top.</p>
      <p>When two closed boxes have several flows between their contents, one line joins them, and its number is the count of flows. Click the line to see the list. Click a box to fade everything that is not connected to it.</p>
      <h2>How a line is drawn</h2>
      <table><tbody>
      <tr><th>Colour</th><td>What passes: blue for an authority (allotment, NCA), green for a document, grey for data, orange for money.</td></tr>
      <tr><th>Pattern</th><td>How it passes: dotted for paper, dashed when a person types, uploads or downloads it, thick for a program-to-program interface or a payment network, thin and solid when an electronic channel is described without its kind, or when the sources do not say.</td></tr>
      <tr><th>Arrow</th><td>A hollow arrow is a plan.</td></tr>
      <tr><th>Faint</th><td>Described by a rule or the owner, use not verified.</td></tr></tbody></table>
      <p>The atlas uses one word, the carrier, for how a flow passes. Here it is split into two questions: who moves the content (a program, the sender's staff, the receiver's staff, the own staff) and the medium (paper, data entry, file, API, payment network). The carrier of the atlas is kept beside the two answers.</p>
      <h2>Cohorts</h2>
      <p>The same act happens in different systems in different agencies. Three cohorts are used:</p>
      <table><tbody>${coh}</tbody></table>
      <h2>Process nets</h2>
      <p>The second view has two kinds of Petri net. The curated chains (spending, release, procurement, collections, taxes, borrowing, reporting, planning) have one net for each cohort; their places are states, balances and records on their way, and each such record is named after its flow in the map. The workflow nets are made from the twenty sequence diagrams of the atlas, and each generated workflow net passed a bounded, finite-state soundness check. That result does not demonstrate operational compliance or correct transaction amounts.</p>
      <h2>What has been verified?</h2>
      <p>Links to statutes, circulars and agency statements establish what those sources say; they do not establish live deployment or a tested data interface. The individual review notices in the map distinguish corroborated descriptions, qualified claims, unresolved deployment questions and modelling inferences. Unreviewed entries are marked as such.</p>
      <p>See <a href="EVIDENCE_REVIEW.md">EVIDENCE_REVIEW.md</a> in the repository for the dated audit and its limitations.</p>
      <h2>Rules of evidence</h2>
      <ul>
        <li>"Not stated" never means "absent". It means that the sources read do not say.</li>
        <li>"GK" means general knowledge that was not read in a source. It is marked wherever it is used.</li>
        <li>"Planned" is never shown as "in use", and two systems drawn near each other are not taken as connected.</li>
        <li>Where sources disagree, the open questions list both.</li>
      </ul>
      <h2>Files</h2>
      <p>The repository holds the registers as CSV files (model/), the Petri nets as PNML files (petri/), the ICONIX domain model, use cases, robustness and sequence diagrams as PlantUML files (iconix/), and static maps (maps/). This page is built from the same registers.</p>
      <p class="note">Facts as of ${esc(D.as_of)}. This is an independent reference, not an official publication of the Philippine government.</p></div>`;
  }

  // --------------------------------------------------------------- tabs and start
  function showTab(name) {
    ["map", "nets", "lists", "about"].forEach((t) => {
      $("tab-" + t).hidden = t !== name;
      $("t-" + t).setAttribute("aria-selected", String(t === name));
    });
    if (name === "map" && cy) { cy.resize(); }
    if (name === "nets") { if (!cyn) openNet(netState.id, netState.cohort, null); else cyn.resize(); }
    try { history.replaceState(null, "", "#" + name); } catch (e) { /* ignore */ }
  }
  function restyle() {
    readTokens();
    if (cy) { cy.style(mapStyle()); renderMap(); }
    if (cyn) { cyn.style(netStyle()); openNet(netState.id, netState.cohort, null); }
    buildLegend();
  }

  function updateThemeButton() {
    const dark = document.documentElement.getAttribute("data-theme") === "dark";
    $("theme-toggle").textContent = dark ? "Light mode" : "Dark mode";
    $("theme-toggle").setAttribute("aria-pressed", String(dark));
    $("theme-toggle").setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
  }
  function start() {
    updateThemeButton();
    $("theme-toggle").addEventListener("click", () => {
      const dark = document.documentElement.getAttribute("data-theme") === "dark";
      if (dark) document.documentElement.removeAttribute("data-theme");
      else document.documentElement.setAttribute("data-theme", "dark");
      try { localStorage.setItem("pfm-theme", dark ? "light" : "dark"); } catch (e) {}
      updateThemeButton();
    });
    $("sub").textContent = `${D.nodes.filter((n) => n.type === "system").length} systems, ${D.flows.length} flows, ${D.records.length} records, ${D.transitions.length + D.sequences.reduce((a, s) => a + s.transitions.length, 0)} transitions in process nets. Facts as of ${D.as_of}.`;
    ["map", "nets", "lists", "about"].forEach((t) => $("t-" + t).addEventListener("click", () => showTab(t)));
    document.querySelectorAll("#levels button").forEach((b) => b.addEventListener("click", () => { setLevel(+b.dataset.level); renderMap({ fit: true }); }));
    $("cohort").addEventListener("change", (e) => { state.cohort = e.target.value; renderMap(); });
    $("showSteps").addEventListener("change", (e) => { state.showSteps = e.target.checked; buildLegend(); renderMap(); });
    $("showAdjacent").addEventListener("change", (e) => { state.showAdjacent = e.target.checked; renderMap(); });
    $("zin").addEventListener("click", () => cy.zoom({ level: cy.zoom() * 1.25, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }));
    $("zout").addEventListener("click", () => cy.zoom({ level: cy.zoom() / 1.25, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }));
    $("zfit").addEventListener("click", () => cy.fit(cy.elements(), 30));
    $("nzin").addEventListener("click", () => cyn && cyn.zoom({ level: cyn.zoom() * 1.25, renderedPosition: { x: cyn.width() / 2, y: cyn.height() / 2 } }));
    $("nzout").addEventListener("click", () => cyn && cyn.zoom({ level: cyn.zoom() / 1.25, renderedPosition: { x: cyn.width() / 2, y: cyn.height() / 2 } }));
    $("nzfit").addEventListener("click", () => cyn && cyn.fit(cyn.elements(), 30));
    buildFilters(); buildLegend(); buildSearch(); buildNetSelect(); buildLists(); buildAbout();
    setLevel(0);
    renderMap({ fit: true });
    panelOverview();
    const h = (location.hash || "").replace("#", "");
    if (["nets", "lists", "about"].includes(h)) showTab(h);
    // Link from the research portal: visualizer.html#find=F032 shows that flow, box or record on the map.
    const findFromHash = () => {
      const m = /^find=(.+)$/.exec((location.hash || "").replace("#", ""));
      if (!m) return;
      const v = decodeURIComponent(m[1]);
      showTab("map");
      $("q").value = v;
      runSearch(v);
      // showTab() replaces the hash with #map; keep the shareable identifier.
      try { history.replaceState(null, "", "#find=" + encodeURIComponent(v)); } catch (e) { /* ignore */ }
    };
    findFromHash();
    window.addEventListener("hashchange", findFromHash);
    try {
      new MutationObserver(restyle).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    } catch (e) { /* ignore */ }
  }
  // handle for tests and for the browser console
  window.PFMAPP = { map: () => cy, net: () => cyn, state };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(start, start); else start();
})();
