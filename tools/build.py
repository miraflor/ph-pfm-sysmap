"""Build every output of the repository from the registers of model/.

Usage:
  python tools/build.py                 check the registers, then write maps/, petri/, iconix/, docs/index.html (research portal),
                                        docs/visualizer.html (interactive map), docs/assets/ and REPORT.md
  python tools/build.py --page-only     check, then write docs/index.html, docs/visualizer.html and docs/assets/ only
  python tools/build.py --cdn PATH      also write a copy of the page that loads Cytoscape.js from a CDN instead of docs/vendor/,
                                        without the document skeleton (for a host that adds it, such as a published artifact)

Needs Python 3.9 or later and Graphviz (the program dot). PlantUML is optional: when the environment variable PLANTUML_JAR names a
plantuml.jar file and Java is installed, the ICONIX diagrams are also rendered to SVG. Without it the .puml files are still written.
"""

import argparse
import collections
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pfmmap import iconix, maps, petri, schema, site  # noqa: E402
from pfmmap.model import ROOT, Model, cohorts_of, split  # noqa: E402
from pfmmap.validate import check  # noqa: E402

AS_OF = "2026-10-13"
CYTOSCAPE_VERSION = "3.33.1"
CYTOSCAPE_CDN = f"https://cdn.jsdelivr.net/npm/cytoscape@{CYTOSCAPE_VERSION}/dist/cytoscape.min.js"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def clean(folder, keep=()):
    """Remove the generated files of a folder, but keep the files named in keep."""
    if not folder.exists():
        return
    for p in folder.iterdir():
        if p.name in keep:
            continue
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()


# ===================================================================== maps

def build_maps(m, out):
    clean(out, keep=("README.md",))
    made = []
    flows_all = maps.visible_flows(m, include_planned=True)
    flows_now = maps.visible_flows(m, include_planned=False)
    dot, agg = maps.dot_level0(m, flows_all)
    maps.render(dot, out / "L0_institutions.svg")
    made.append(("L0_institutions.svg", "Level 0: institutions and parties; one line for each pair, with the number of flows", len(flows_all)))
    maps.render(maps.dot_detail(m, flows_now, 1, "Level 1. Systems and units, flows in use, in part or described (plans left out)", "L1now"),
                out / "L1_systems_now.svg")
    made.append(("L1_systems_now.svg", "Level 1: systems and units, without the planned flows", len(flows_now)))
    maps.render(maps.dot_detail(m, flows_all, 1, "Level 1. Systems and units, with the planned flows (hollow arrows)", "L1all"),
                out / "L1_systems_with_plans.svg")
    made.append(("L1_systems_with_plans.svg", "Level 1: systems and units, with the planned flows", len(flows_all)))
    maps.render(maps.dot_detail(m, flows_all, 2, "Level 2. Modules, where a system has modules", "L2"), out / "L2_modules.svg")
    made.append(("L2_modules.svg", "Level 2: modules of BTMS, PhilGEPS and other systems", len(flows_all)))
    names = {v["value"]: v["meaning"] for v in m.t["vocab"] if v["table"] == "flows" and v["column"] == "domain"}
    for dom in sorted({f["domain"] for f in flows_all}):
        fl = [f for f in flows_all if f["domain"] == dom]
        title = f"Level 1. {names.get(dom, dom)} ({len(fl)} flows)"
        maps.render(maps.dot_detail(m, fl, 1, title, "D_" + dom), out / "by_domain" / f"L1_{dom}.svg")
        made.append((f"by_domain/L1_{dom}.svg", f"Level 1, one part of PFM: {names.get(dom, dom)}", len(fl)))
    adj = [f for f in maps.visible_flows(m, include_planned=True, include_adjacent=True) if f not in flows_all]
    if adj:
        maps.render(maps.dot_detail(m, adj, 1, "Level 1. Flows that touch systems adjacent to PFM", "ADJ"), out / "L1_adjacent.svg")
        made.append(("L1_adjacent.svg", "Level 1: flows that touch systems adjacent to PFM", len(adj)))
    return made


# ===================================================================== petri nets

def seq_pnml(net):
    places = [{"id": p["id"], "name": p["name"], "initial": p.get("initial", "")} for p in net.places]
    trans = [{"id": t["id"], "name": t["name"]} for t in net.trans]
    return petri.pnml(f"SEQ-{net.did}", f"{net.did} {net.title}", places, trans, net.arcs)


def build_petri(m, out):
    clean(out, keep=("README.md",))
    chains = []
    for c in m.t["chains"] + [{"chain_id": None, "name": "All chains together"}]:
        for coh in ("P", "E", "B"):
            if not m.transitions_of(c["chain_id"], coh):
                continue
            net = petri.chain_net(m, c["chain_id"], coh)
            title = f"{net['id']}: {c['name']} (cohort {coh})"
            write(out / "chains" / f"{net['id']}.pnml", petri.chain_pnml(m, net, title))
            maps.render(petri.chain_dot(m, net, title), out / "chains" / f"{net['id']}.svg")
            ana = petri.chain_analysis(net)
            reads = sum(1 for a in net["arcs"] if a["direction"] == "read")
            chains.append({"id": net["id"], "name": c["name"], "cohort": coh, "places": len(net["places"]), "transitions": len(net["transitions"]),
                           "arcs": len(net["arcs"]), "reads": reads, "sources": ana["sources"], "sinks": ana["sinks"]})
    seqs = []
    for did in sorted(m.sequences):
        net = petri.build_seq(m, did)
        snd = petri.soundness(net)
        write(out / "sequences" / f"{did}.pnml", seq_pnml(net))
        maps.render(petri.seq_dot(net), out / "sequences" / f"{did}.svg")
        seqs.append({"id": did, "title": net.title, "steps": sum(1 for t in net.trans if not t["silent"]),
                     "silent": sum(1 for t in net.trans if t["silent"]), "places": len(net.places), **snd})
    windows = {}
    for r in m.t["rules"]:
        places = split(r["places"])
        if r["kind"] != "invariant" or not places:
            continue
        for coh in ("P", "E", "B"):
            windows[(r["rule_id"], coh)] = (places, petri.difference_windows(m, places, coh))
    write(out / "ANALYSIS.md", petri_analysis_md(m, chains, seqs, windows))
    return chains, seqs, windows


def petri_analysis_md(m, chains, seqs, windows):
    P = m.ix["places"]
    L = ["# Analysis of the process nets", "",
         "This file is written by tools/build.py. Do not edit it by hand.", "",
         "## Curated chain nets", "",
         "One net for each chain and cohort. A place with no input is where the chain starts (a source); a place with no output is where it ends (a sink). A read arc needs a token and leaves it. In PNML a read arc is written as two arcs, one in each direction.", "",
         "| Net | Chain | Places | Transitions | Arcs | Read arcs | Sources | Sinks |", "|---|---|---|---|---|---|---|---|"]
    for c in chains:
        L.append(f"| {c['id']} | {c['name']} | {c['places']} | {c['transitions']} | {c['arcs']} | {c['reads']} | {', '.join(c['sources'])} | {', '.join(c['sinks'])} |")
    L += ["", "## Windows in which the NCA balances differ", "",
          "Rule R-NCA-EQUAL is a reconciliation objective, not a claim of identical balances at every moment. The listed transitions touch some but not all of the corresponding record places. That structural observation identifies possible timing differences, not measured monetary discrepancies or proof that a real reconciliation succeeds. The rule is a modelling inference; these ordinary PT nets do not encode monetary values or UACS dimensions.", ""]
    for (rid, coh), (places, wins) in sorted(windows.items(), key=lambda x: x[0][1]):
        live = [p for p in places if coh in cohorts_of(P[p]["cohorts"])]
        L.append(f"### Cohort {coh}: {len(live)} places ({', '.join(live)})")
        L.append("")
        if not wins:
            L.append("No transition changes one place without the others.")
        for tid, name, changed in wins:
            L.append(f"- {tid} {name}: changes {', '.join(changed)} only")
        L.append("")
    L += ["## Workflow nets of the atlas sequence diagrams", "",
          "Each sequence diagram of the atlas is turned into a workflow net: one start place, one end place, a transition for each message or own action, and silent transitions for the blocks (alt is an exclusive choice, opt is a choice with a silent skip, par is a split and a join, loop is repeat or exit). Blocks of the kind break, critical and rect are taken in sequence. The check searches all reachable markings. A net is sound when every reachable marking can reach the end, the end is reached with no other token left, every transition can fire, and no place ever holds two tokens.", "",
          "| Diagram | Title | Steps | Silent | Places | Markings | Sound |", "|---|---|---|---|---|---|---|"]
    for s in seqs:
        L.append(f"| {s['id']} | {s['title']} | {s['steps']} | {s['silent']} | {s['places']} | {s.get('states', '')} | {'yes' if s.get('sound') else 'NO'} |")
    L.append("")
    return "\n".join(L)


# ===================================================================== ICONIX

def plantuml_available():
    jar = os.environ.get("PLANTUML_JAR", "")
    return bool(jar) and Path(jar).exists() and bool(shutil.which("java"))


def plantuml_render(files):
    jar = os.environ.get("PLANTUML_JAR", "")
    if not plantuml_available() or not files:
        return False
    env = dict(os.environ)
    if shutil.which("dot"):
        env["GRAPHVIZ_DOT"] = shutil.which("dot")
    for i in range(0, len(files), 40):
        batch = [str(f) for f in files[i:i + 40]]
        res = subprocess.run(["java", "-Djava.awt.headless=true", "-jar", jar, "-tsvg", "-charset", "UTF-8"] + batch,
                             capture_output=True, env=env, timeout=900)
        if res.returncode != 0:
            raise RuntimeError("PlantUML render failed: " + (res.stderr + res.stdout).decode("utf-8", "replace")[:1000])
        missing = [str(f) for f in files[i:i + 40] if not f.with_suffix(".svg").exists()]
        if missing:
            raise RuntimeError("PlantUML did not produce required SVGs: " + ", ".join(missing[:6]))
    return True


def use_case_md(m, ucs_out, bucs):
    L = ["# ICONIX use cases", "",
         "This file is written by tools/build.py from model/use_cases.csv, model/transitions.csv, model/bindings.csv and the sequence diagrams of the atlas. Do not edit it by hand.", "",
         "There are two kinds of use case here.", "",
         "System use cases follow the curated chains of the process nets. Each one is a group of transitions with one goal. It is written once for each group of cohorts in which the same acts happen through the same boundary and control objects. The boundary object is what the actor touches (a form, a screen, a portal). The control object is the check of the step, done by a person, by software or by the bank. The entity objects are the records that the step uses or writes, with the body or system that holds them in that cohort.", "",
         "Business use cases are made from the twenty sequence diagrams of the atlas. Their basic course is the first branch of every choice; the other branches and the optional blocks are the alternate courses.", "",
         "## System use cases", ""]
    for uc, variants in ucs_out:
        L.append(f"### {uc['use_case_id']} {uc['name']}")
        L.append("")
        L.append(f"Chain: {uc['chain_id']} ({m.ix['chains'][uc['chain_id']]['name']}). Primary actor: {m.ix['roles'][uc['primary_role']]['name']}.")
        L.append("")
        L.append(f"Goal: {uc['goal']}")
        L.append("")
        for cohorts, tids, files in variants:
            c = cohorts[0]
            L.append(f"Basic course in cohort {', '.join(cohorts)} (diagrams: {', '.join(files)}):")
            L.append("")
            for i, tid in enumerate(tids, 1):
                t = m.ix["transitions"][tid]
                b = m.binding(tid, c) or {}
                role = m.ix["roles"][t["role_id"]]["name"]
                ctrl = {"person": "a person checks", "software": "software checks", "bank": "the bank checks", "not_stated": "the check is not stated"}.get(b.get("controller_kind", ""), "")
                writes = ", ".join(m.label(n) for n in split(b.get("writes_in", "")))
                ents = "; ".join(m.ix["records"][r]["name"] + (f" [{m.label(h)}]" if h else "") for r, h in iconix.entity_records(m, tid, c))
                L.append(f"{i}. {role}: {t['name']} ({tid}). Boundary: {b.get('boundary', 'not stated')}. Control: {b.get('controller', 'not stated')}, {ctrl}." + (f" Writes in: {writes}." if writes else "") + (f" Records: {ents}." if ents else ""))
            L.append("")
        alts = [a.strip() for a in uc["alternate_courses"].split(" | ") if a.strip()]
        if alts:
            L.append("Alternate courses:")
            L.append("")
            for a in alts:
                L.append(f"- {a}")
            L.append("")
    L += ["## Business use cases from the sequence diagrams of the atlas", ""]
    L += bucs
    return "\n".join(L)


def build_iconix(m, out):
    if plantuml_available():
        clean(out, keep=("README.md",))
    else:
        # Without PlantUML the drawings cannot be made again: keep the SVG files of the last build.
        for p in list(out.rglob("*.puml")) + [out / "USE_CASES.md"]:
            if p.exists():
                p.unlink()
        print("  PlantUML not found (set PLANTUML_JAR): the .puml files are written, the SVG drawings are those of the last build")
    pumls = []
    records = sorted({f["record_id"] for f in m.t["fields"]} | {l["from_record"] for l in m.t["record_links"]} | {l["to_record"] for l in m.t["record_links"]})
    write(out / "domain_model.puml", iconix.domain_model(m, records, "Domain model: the records of diagram 17c of the atlas and their links"))
    pumls.append(out / "domain_model.puml")
    write(out / "use_case_diagram.puml", iconix.use_case_diagram(m, m.t["use_cases"], "System use cases of the curated chains"))
    pumls.append(out / "use_case_diagram.puml")
    bad_links = []
    ucs_out = []
    for uc in m.t["use_cases"]:
        variants = []
        for cohorts, tids in iconix.use_case_cohorts(m, uc):
            tag = "".join(cohorts)
            name = f"{uc['use_case_id']}_{tag}"
            rob = iconix.robustness(m, uc, cohorts, tids)
            bad = iconix.check_robustness_rules(rob)
            bad_links += [(name, b) for b in bad]
            write(out / "robustness" / f"{name}.puml", rob)
            write(out / "sequence" / f"{name}.puml", iconix.sequence(m, uc, cohorts, tids))
            pumls += [out / "robustness" / f"{name}.puml", out / "sequence" / f"{name}.puml"]
            variants.append((cohorts, tids, [f"robustness/{name}", f"sequence/{name}"]))
        ucs_out.append((uc, variants))
    bucs = [iconix.business_use_case(m, did) for did in sorted(m.sequences)]
    write(out / "USE_CASES.md", use_case_md(m, ucs_out, bucs))
    rendered = plantuml_render(pumls)
    return {"puml": len(pumls), "rendered": rendered, "bad_links": bad_links, "variants": sum(len(v) for _, v in ucs_out)}


# ===================================================================== page

def build_page(m, cdn_path=None, fresh_iconix_svg=False):
    from verification_inventory import build as build_review_queue
    build_review_queue()
    # Published evidence notes must follow the source review, not an old manual copy.
    shutil.copyfile(ROOT / "EVIDENCE_REVIEW.md", ROOT / "docs" / "EVIDENCE_REVIEW.md")
    data = site.build_data(m, AS_OF)
    vendor = ROOT / "docs" / "vendor"
    if not (vendor / "cytoscape.min.js").exists():
        print("  docs/vendor/cytoscape.min.js is missing. Get it with: npm pack cytoscape@" + CYTOSCAPE_VERSION)
    size = site.write_page(data, ROOT / "tools" / "site", ROOT / "docs" / "visualizer.html", ["vendor/cytoscape.min.js"])
    out = [("docs/visualizer.html", size)]
    if cdn_path:
        size2 = site.write_page(data, ROOT / "tools" / "site", Path(cdn_path), [CYTOSCAPE_CDN], standalone=False)
        out.append((str(cdn_path), size2))
    from portal import build as build_portal
    homepage_size = build_portal(ROOT, AS_OF, fresh_iconix_svg=fresh_iconix_svg)
    out.append(("docs/index.html", homepage_size))
    return data, out


# ===================================================================== report

def report_md(m, made_maps, chains, seqs, windows, ico, page):
    t = m.t
    C = collections.Counter
    sysn = [n for n in t["nodes"] if n["type"] == "system"]
    flows = t["flows"]
    ev = C(m.evidence(f["basis"])["best"] for f in flows)
    gk = sum(1 for f in flows if m.evidence(f["basis"])["has_gk"])
    linked = sum(1 for s in t["steps"] if split(s["flows"]))
    own = sum(1 for s in t["steps"] if s["own_action"] == "yes")
    L = ["# Report of the build", "",
         f"Written by tools/build.py. Facts as of {AS_OF}.", "",
         "## Registers", "",
         "| Register | Rows |", "|---|---|"]
    for k, v in t.items():
        L.append(f"| model/{k}.csv | {len(v)} |")
    L += ["", "## Boxes of the map", "", "| Level | Type | Count |", "|---|---|---|"]
    for (lv, ty), n in sorted(C((x["level"], x["type"]) for x in t["nodes"]).items()):
        L.append(f"| {lv} | {ty} | {n} |")
    L += ["", "Systems by status:", ""]
    for s, n in C(x["status"] or "none" for x in sysn).most_common():
        L.append(f"- {s}: {n}")
    L += ["", "## Flows", "",
          f"{len(flows)} flows. {sum(1 for f in flows if f['atlas_row'])} come from the {len({f['atlas_row'] for f in flows if f['atlas_row']})} rows of the register of the atlas (some rows are split in two or three). {sum(1 for f in flows if not f['atlas_row'])} are new in this repository.", ""]
    for col in ("kind", "stage", "agent", "medium", "domain"):
        L.append(f"By {col}: " + ", ".join(f"{k} {v}" for k, v in C(f[col] for f in flows).most_common()) + ".")
        L.append("")
    L.append("Strongest source of each flow: " + ", ".join(f"{k} {v}" for k, v in ev.most_common()) + f". Flows whose basis includes general knowledge (GK): {gk}.")
    L += ["", "## Process steps", "",
          f"{len(t['steps'])} steps from {len(m.sequences)} sequence diagrams of the atlas. {own} are own actions (a body acts alone). {linked} are linked to a flow of the register. The other steps pass a document or a request that the register does not list as a flow between systems; the map shows them when you tick Process steps.", "",
          "## Maps", "", "| File | What it shows | Flows |", "|---|---|---|"]
    for f, what, n in made_maps:
        L.append(f"| maps/{f} | {what} | {n} |")
    L += ["", "## Process nets", "",
          f"{len(chains)} curated chain nets (chains by cohort, and all chains together by cohort) and {len(seqs)} workflow nets of the sequence diagrams. Sound *generated block-structured workflow nets* under the finite-state model: {sum(1 for s in seqs if s.get('sound'))} of {len(seqs)}; this does not prove the real government processes correct or their financial values consistent. Details in petri/ANALYSIS.md.", ""]
    for (rid, coh), (places, wins) in sorted(windows.items(), key=lambda x: x[0][1]):
        L.append(f"- {rid}, cohort {coh}: {len(wins)} transitions touch a subset of NCA-record places (potential reconciliation timing windows; amounts not simulated).")
    L += ["", "## ICONIX", "",
          f"{len(t['use_cases'])} system use cases, drawn in {ico['variants']} cohort variants (robustness and sequence diagram for each), {len(m.sequences)} business use cases, one domain model and one use case diagram: {ico['puml']} PlantUML files. Links that break the four rules of robustness diagrams: {len(ico['bad_links'])}. SVG drawings: {'rendered from current .puml sources' if ico['rendered'] else 'not rerendered (PlantUML was not configured; existing SVGs may be stale)'}.", "",
          "## Open questions", "", "| Status | Count |", "|---|---|"]
    for s, n in C(g["status"] for g in t["gaps"]).most_common():
        L.append(f"| {s} | {n} |")
    L += ["", "## Page", ""]
    for p, size in page:
        if p == "docs/index.html":
            L.append(f"- {p}: {size / 1024:.0f} KB, standalone research portal with the source registers")
        if p == "docs/visualizer.html":
            L.append(f"- {p}: {size / 1024:.0f} KB, original map and process-net viewer")
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page-only", action="store_true")
    ap.add_argument("--cdn", help="also write a copy of the page that loads Cytoscape.js from a CDN")
    a = ap.parse_args()
    m = Model()
    problems, warnings = check(m)
    for w in warnings:
        print("warning:", w)
    if problems:
        for p in problems:
            print("problem:", p)
        print(f"Problems found: {len(problems)}. Nothing was built.")
        return 1
    for line in schema.undocumented(m):
        print("warning:", line)
    print("Checks: no problems")
    if a.page_only:
        _, page = build_page(m, a.cdn)
        for p, size in page:
            print(f"page: {p} ({size / 1024:.0f} KB)")
        return 0
    made = build_maps(m, ROOT / "maps")
    print(f"maps: {len(made)} SVG files")
    chains, seqs, windows = build_petri(m, ROOT / "petri")
    print(f"petri: {len(chains)} chain nets, {len(seqs)} workflow nets, sound {sum(1 for s in seqs if s.get('sound'))}")
    ico = build_iconix(m, ROOT / "iconix")
    print(f"iconix: {ico['puml']} PlantUML files, rule breaks {len(ico['bad_links'])}, rendered {ico['rendered']}")
    for name, line in ico["bad_links"]:
        print("  robustness rule broken in", name, ":", line)
    _, page = build_page(m, a.cdn, fresh_iconix_svg=ico["rendered"])
    for p, size in page:
        print(f"page: {p} ({size / 1024:.0f} KB)")
    write(ROOT / "docs" / "DATA_MODEL.md", schema.data_model_md(m))
    print("docs/DATA_MODEL.md written")
    write(ROOT / "REPORT.md", report_md(m, made, chains, seqs, windows, ico, page))
    print("REPORT.md written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
