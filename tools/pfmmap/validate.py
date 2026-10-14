"""Checks of the registers. Each problem is one line; the build stops if there is any problem."""

import re

from .model import cohorts_of, split

REQUIRED_BASIS = ["nodes", "flows", "records", "places", "transitions", "rules", "roles", "bindings", "place_holders"]


def check(m):
    problems = []
    warnings = []
    P = problems.append

    def exists(table, value, where):
        if value and value not in m.ix[table]:
            P(f"{where}: '{value}' is not a known {table[:-1] if table.endswith('s') else table} id")

    # vocabularies
    def voc(table, column, rows, multi=False, allow_empty=False):
        allowed = m.vocab(table, column)
        for r in rows:
            vals = split(r[column]) if multi else [r[column]]
            for v in vals:
                if v == "" and allow_empty:
                    continue
                if v not in allowed:
                    P(f"{table}.{column}: value '{v}' is not in vocab.csv (row {r.get(list(r)[0])})")

    voc("nodes", "level", m.t["nodes"])
    voc("nodes", "type", m.t["nodes"])
    voc("nodes", "status", m.t["nodes"], allow_empty=True)
    voc("nodes", "scope", m.t["nodes"])
    for col in ("kind", "agent", "medium", "stage", "domain"):
        voc("flows", col, m.t["flows"])
    voc("records", "kind", m.t["records"])
    voc("places", "kind", m.t["places"])
    voc("places", "line", m.t["places"])
    voc("arcs", "direction", m.t["arcs"])
    voc("bindings", "controller_kind", m.t["bindings"])
    voc("rules", "kind", m.t["rules"])
    voc("gaps", "status", m.t["gaps"])
    voc("sources", "type", m.t["sources"])
    voc("roles", "kind", m.t["roles"])
    cohort_ok = {"P", "E", "B", "all"}
    for table, col in (("flows", "cohorts"), ("places", "cohorts"), ("transitions", "cohorts"), ("arcs", "cohorts")):
        for r in m.t[table]:
            for v in split(r[col]) or ["all"]:
                if v not in cohort_ok:
                    P(f"{table}.{col}: unknown cohort '{v}'")
    for table in ("bindings", "place_holders"):
        for r in m.t[table]:
            if r["cohort"] not in cohort_ok:
                P(f"{table}.cohort: unknown cohort '{r['cohort']}'")

    # nodes
    for n in m.t["nodes"]:
        if n["parent_id"]:
            exists("nodes", n["parent_id"], f"node {n['node_id']} parent")
            if n["parent_id"] in m.ix["nodes"] and int(m.ix["nodes"][n["parent_id"]]["level"]) != int(n["level"]) - 1:
                P(f"node {n['node_id']}: level {n['level']} under a parent of level {m.ix['nodes'][n['parent_id']]['level']}")
        elif n["level"] != "0":
            P(f"node {n['node_id']}: level {n['level']} without a parent")

    # flows
    for f in m.t["flows"]:
        for c in ("from_id", "via_id", "to_id"):
            exists("nodes", f[c], f"flow {f['flow_id']} {c}")
        for r in split(f["payload"]):
            exists("records", r, f"flow {f['flow_id']} payload")
        for g in split(f["gaps"]):
            exists("gaps", g, f"flow {f['flow_id']} gaps")
        if f["kind"] == "money" and f["medium"] not in ("bank_transfer", "cash_or_check", "payment_network"):
            P(f"flow {f['flow_id']}: money with medium {f['medium']}")
        if f["from_id"] == f["to_id"]:
            P(f"flow {f['flow_id']}: from and to are the same node")

    # records, fields, links
    for r in m.t["records"]:
        exists("nodes", r["issuer_node"], f"record {r['record_id']} issuer_node")
    for fl in m.t["fields"]:
        exists("records", fl["record_id"], "field record")
        exists("records", fl["references"], f"field {fl['record_id']}.{fl['field']} references")
    for lk in m.t["record_links"]:
        exists("records", lk["from_record"], f"link {lk['link_id']}")
        exists("records", lk["to_record"], f"link {lk['link_id']}")

    # roles, actors, steps
    for r in m.t["roles"]:
        exists("nodes", r["node_id"], f"role {r['role_id']}")
    for a in m.t["actor_map"]:
        exists("nodes", a["node_id"], f"actor '{a['atlas_actor']}'")
        exists("roles", a["role_id"], f"actor '{a['atlas_actor']}'")
    for s in m.t["steps"]:
        exists("nodes", s["who_node"], f"step {s['step_id']} who")
        exists("nodes", s["to_node"], f"step {s['step_id']} to")
        exists("roles", s["who_role"], f"step {s['step_id']} who_role")
        exists("roles", s["to_role"], f"step {s['step_id']} to_role")
        for f in split(s["flows"]):
            exists("flows", f, f"step {s['step_id']} flows")

    # chains
    for p in m.t["places"]:
        exists("flows", p["flow_id"], f"place {p['place_id']} flow")
        for r in split(p["records"]):
            exists("records", r, f"place {p['place_id']} records")
        if p["kind"] == "channel" and not p["flow_id"]:
            P(f"place {p['place_id']}: a channel without a flow")
    for h in m.t["place_holders"]:
        exists("places", h["place_id"], "holder place")
        exists("nodes", h["held_in"], f"holder of {h['place_id']}")
    for t in m.t["transitions"]:
        exists("chains", t["chain_id"], f"transition {t['transition_id']} chain")
        exists("roles", t["role_id"], f"transition {t['transition_id']} role")
        exists("nodes", t["node_id"], f"transition {t['transition_id']} node")
        for s in split(t["steps"]):
            exists("steps", s, f"transition {t['transition_id']} steps")
        for r in split(t["rules"]):
            exists("rules", r, f"transition {t['transition_id']} rules")
        ins = [a for a in m.t["arcs"] if a["transition_id"] == t["transition_id"]]
        if not any(a["direction"] == "out" for a in ins):
            P(f"transition {t['transition_id']}: no output place")
        if not any(a["direction"] in ("in", "read") for a in ins):
            P(f"transition {t['transition_id']}: no input place")
    for a in m.t["arcs"]:
        exists("transitions", a["transition_id"], "arc transition")
        exists("places", a["place_id"], f"arc of {a['transition_id']}")
        if a["transition_id"] in m.ix["transitions"] and a["place_id"] in m.ix["places"]:
            tc = set(cohorts_of(m.ix["transitions"][a["transition_id"]]["cohorts"]))
            pc = set(cohorts_of(m.ix["places"][a["place_id"]]["cohorts"]))
            ac = set(cohorts_of(a["cohorts"])) if a["cohorts"] not in ("", "all") else tc
            if not ac <= tc:
                P(f"arc {a['transition_id']}->{a['place_id']}: cohorts {sorted(ac)} not in the cohorts of the transition {sorted(tc)}")
            if not (ac & tc) <= pc:
                P(f"arc {a['transition_id']}->{a['place_id']}: place {a['place_id']} does not exist in cohorts {sorted((ac & tc) - pc)}")
    for b in m.t["bindings"]:
        exists("transitions", b["transition_id"], "binding")
        exists("nodes", b["boundary_node"], f"binding of {b['transition_id']} boundary_node")
        for n in split(b["writes_in"]):
            exists("nodes", n, f"binding of {b['transition_id']} writes_in")
    for r in m.t["rules"]:
        for t in split(r["transitions"]):
            exists("transitions", t, f"rule {r['rule_id']}")
        for pl in split(r["places"]):
            exists("places", pl, f"rule {r['rule_id']} places")
        if r["places"] and r["kind"] != "invariant":
            P(f"rule {r['rule_id']}: only an invariant names places")
    for t in m.t["transitions"]:
        for c in cohorts_of(t["cohorts"]):
            if not m.binding(t["transition_id"], c):
                P(f"transition {t['transition_id']}: no binding for cohort {c}")

    # use cases
    for u in m.t["use_cases"]:
        exists("chains", u["chain_id"], f"use case {u['use_case_id']} chain")
        exists("roles", u["primary_role"], f"use case {u['use_case_id']} primary_role")
        tids = split(u["transitions"])
        if not tids:
            P(f"use case {u['use_case_id']}: no transitions")
        for t in tids:
            exists("transitions", t, f"use case {u['use_case_id']}")
            if t in m.ix["transitions"] and m.ix["transitions"][t]["chain_id"] != u["chain_id"]:
                P(f"use case {u['use_case_id']}: transition {t} belongs to {m.ix['transitions'][t]['chain_id']}, not {u['chain_id']}")
    covered = {t for u in m.t["use_cases"] for t in split(u["transitions"])}
    for t in m.t["transitions"]:
        if t["transition_id"] not in covered:
            warnings.append(f"transition {t['transition_id']} is in no use case")

    # gaps
    for g in m.t["gaps"]:
        for r in split(g["related"]):
            if r not in m.ix["nodes"] and r not in m.ix["flows"] and r not in m.ix["records"]:
                P(f"gap {g['gap_id']}: related '{r}' is not a node, flow or record")

    # basis: every row with a basis names at least one known source
    for table in REQUIRED_BASIS:
        for r in m.t[table]:
            b = r.get("basis", "")
            if not b:
                if table in ("nodes",) and r["type"] in ("institution", "external", "unit"):
                    P(f"{table} {list(r.values())[0]}: empty basis")
                elif table != "nodes":
                    P(f"{table} {list(r.values())[0]}: empty basis")
                continue
            if not m.codes_in(b):
                P(f"{table} {list(r.values())[0]}: basis '{b}' names no known source code")
    # codes that look like source codes but are unknown
    known = set(m.ix["sources"])
    token = re.compile(r"\b([A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+|[A-Z]{2,}[0-9]{2,}[A-Z0-9-]*)\b")
    for table in REQUIRED_BASIS + ["gaps", "steps", "fields", "record_links", "cohorts"]:
        for r in m.t[table]:
            for tok in token.findall(r.get("basis", "")):
                if re.match(r"^[IVX]+-[A-D]$", tok):
                    continue
                if tok not in known and not any(tok.startswith(k) for k in known) and not tok.startswith(("R-", "S-", "F0", "F1", "GAP-")):
                    warnings.append(f"{table}: '{tok}' in a basis looks like a source code that is not in sources.csv")
    return problems, sorted(set(warnings))
