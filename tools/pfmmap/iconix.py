"""ICONIX files made from the registers: domain model, actors, use cases, robustness and sequence diagrams.

ICONIX uses four kinds of object. An actor is a person or system outside the system under design. A boundary
object is what the actor touches: a form, a screen, a portal, a file. A control object is the logic of one step:
a check or a calculation. An entity object is a stored record. The rules of a robustness diagram are: an actor
connects only to boundary objects; a boundary object connects to actors and control objects; an entity object
connects only to control objects; control objects connect to boundary objects, entity objects and other control
objects.

Here the "system under design" changes with the cohort. In cohort P the boundary objects are paper forms and
most control objects are persons who sign; in cohort B they are screens and checks of BTMS. The same use case
is therefore drawn once for each cohort in which it exists.
"""

import re

from .model import cohorts_of, split


def pid(s):
    return re.sub(r"[^A-Za-z0-9_]", "_", s)


def short(text, n=60):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def pq(s):
    return '"' + s.replace('"', "'") + '"'


def rec_label(m, rid, n=44):
    """Short name of a record, with its abbreviation first: 'IAR: Inspection and Acceptance Report'."""
    name = re.sub(r",\s*App\.\s*\d+[A-Z]?.*$", "", m.ix["records"][rid]["name"])
    mt = re.search(r"\(([A-Z][A-Za-z0-9-]{1,12})\)", name)
    if mt:
        rest = (name[:mt.start()] + name[mt.end():]).strip(" ,")
        return short(f"{mt.group(1)}: {rest}", n)
    return short(name, n)


# ------------------------------------------------------------------ domain model

def domain_model(m, records=None, title="Domain model"):
    fields = {}
    for f in m.t["fields"]:
        fields.setdefault(f["record_id"], []).append(f)
    links = m.t["record_links"]
    if records is None:
        records = sorted(set(fields) | {l["from_record"] for l in links} | {l["to_record"] for l in links})
    card = {"||--o{": ('"1"', '"0..*"'), "||--|{": ('"1"', '"1..*"'), "||--o|": ('"1"', '"0..1"'), "||--||": ('"1"', '"1"')}
    out = ["@startuml", f"title {title}", "hide methods", "hide circle", "skinparam shadowing false", "skinparam classAttributeIconSize 0",
           "skinparam class {", "  BackgroundColor #FFFFFF", "  BorderColor #555555", "}", "left to right direction"]
    for rid in records:
        r = m.ix["records"][rid]
        out.append(f'class {pq(short(r["name"], 48))} as {pid(rid)} <<{r["kind"]}>> {{')
        for f in sorted(fields.get(rid, []), key=lambda x: int(x["order"])):
            key = f" <<{f['key']}>>" if f["key"] else ""
            gk = " (general knowledge)" if f["basis"] == "GK" else ""
            out.append(f'  {f["field"]} : {f["type"]}{key}{gk}')
        out.append("}")
    for l in links:
        if l["from_record"] in records and l["to_record"] in records:
            a, b = card.get(l["cardinality"], ('"1"', '"*"'))
            lab = l["relation"] + (f" [{l['key']}]" if l["key"] else "") + (" (general knowledge)" if l["basis"] == "GK" else "")
            out.append(f'{pid(l["from_record"])} {a} -- {b} {pid(l["to_record"])} : {pq(short(lab, 48))[1:-1]}')
    out.append("@enduml")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ use cases of the chains

def use_case_cohorts(m, uc):
    tids = split(uc["transitions"])
    variants = {}
    for c in ("P", "E", "B"):
        ts = [t for t in tids if c in cohorts_of(m.ix["transitions"][t]["cohorts"])]
        sig = tuple((t, (m.binding(t, c) or {}).get("boundary", ""), (m.binding(t, c) or {}).get("controller", "")) for t in ts)
        if ts:
            variants.setdefault(sig, []).append(c)
    return [(cs, [s[0] for s in sig]) for sig, cs in variants.items()]


def entity_records(m, tid, cohort):
    out = []
    for a in m.arcs_of(tid, cohort):
        p = m.ix["places"][a["place_id"]]
        if p["kind"] == "clock":
            continue
        for r in split(p["records"]):
            if r not in [x[0] for x in out]:
                h = m.holder(p["place_id"], cohort)
                out.append((r, h["held_in"] if h else ""))
    return out


def robustness(m, uc, cohorts, tids):
    c = cohorts[0]
    out = ["@startuml", f"title {uc['use_case_id']} {uc['name']} (cohort {', '.join(cohorts)})", "left to right direction",
           "skinparam shadowing false", "skinparam defaultFontName Helvetica", "skinparam defaultFontSize 11"]
    declared = set()

    def declare(kind, key, label):
        if key not in declared:
            declared.add(key)
            out.append(f'{kind} {pq(label)} as {key}')

    links = []
    prev_ctrl = None
    for tid in tids:
        t = m.ix["transitions"][tid]
        b = m.binding(tid, c)
        role = m.ix["roles"][t["role_id"]]
        a_key = pid(role["role_id"])
        declare("actor", a_key, short(role["name"], 40))
        bnd_label = short(b["boundary"], 50) if b else "Not stated"
        b_key = pid(f"B_{tid}")
        declare("boundary", b_key, bnd_label)
        who = {"person": "by a person", "software": "by software", "bank": "by the bank", "not_stated": "check not stated"}.get(b["controller_kind"] if b else "", "")
        ctl_key = pid(f"C_{tid}")
        declare("control", ctl_key, short(f"{tid} {t['name']} ({who})", 56))
        links += [(a_key, b_key), (b_key, ctl_key)]
        if prev_ctrl:
            links.append((prev_ctrl, ctl_key))
        prev_ctrl = ctl_key
        for rid, held in entity_records(m, tid, c):
            r = m.ix["records"][rid]
            where = f" [{m.label(held)}]" if held else ""
            e_key = pid(f"E_{rid}_{held}")
            declare("entity", e_key, rec_label(m, rid) + where)
            links.append((ctl_key, e_key))
    seen = set()
    for a, b in links:
        if (a, b) not in seen:
            seen.add((a, b))
            out.append(f"{a} -- {b}")
    out.append("@enduml")
    return "\n".join(out) + "\n"


def check_robustness_rules(text):
    """Return the links of a generated robustness diagram that break the four ICONIX rules."""
    kinds = {}
    for line in text.splitlines():
        mt = re.match(r'^(actor|boundary|control|entity) ".*" as (\S+)$', line)
        if mt:
            kinds[mt.group(2)] = mt.group(1)
    allowed = {("actor", "boundary"), ("boundary", "actor"), ("boundary", "control"), ("control", "boundary"),
               ("control", "entity"), ("entity", "control"), ("control", "control")}
    bad = []
    for line in text.splitlines():
        mt = re.match(r"^(\S+) -- (\S+)$", line)
        if mt and (kinds.get(mt.group(1)), kinds.get(mt.group(2))) not in allowed:
            bad.append(line)
    return bad


def sequence(m, uc, cohorts, tids):
    c = cohorts[0]
    out = ["@startuml", f"title {uc['use_case_id']} {uc['name']} (cohort {', '.join(cohorts)})", "skinparam shadowing false",
           "skinparam defaultFontName Helvetica", "skinparam defaultFontSize 10", "skinparam sequenceMessageAlign left", "autonumber"]
    parts = []

    def part(kind, key, label):
        if key not in [p[1] for p in parts]:
            parts.append((kind, key, label))

    msgs = []
    for tid in tids:
        t = m.ix["transitions"][tid]
        b = m.binding(tid, c)
        role = m.ix["roles"][t["role_id"]]
        a_key = pid(role["role_id"])
        part("actor", a_key, short(role["name"], 30))
        bnode = b["boundary_node"] if b and b["boundary_node"] else ""
        b_key = pid("B_" + (bnode or tid))
        part("boundary", b_key, short(m.label(bnode) if bnode else (b["boundary"] if b else "form"), 34))
        k = b["controller_kind"] if b else "not_stated"
        ctl_key = pid("C_" + ("software_" + bnode if k == "software" and bnode else k + "_" + role["role_id"]))
        ctl_label = {"software": "check by " + (m.label(bnode) if bnode else "software"), "bank": "check by the bank",
                     "person": "check by " + short(role["name"], 26), "not_stated": "check (not stated)"}[k]
        part("control", ctl_key, ctl_label)
        msgs.append(f"== {tid} {short(t['name'], 50)} ==")
        msgs.append(f"{a_key} -> {b_key} : {short(b['boundary'] if b else t['name'], 70)}")
        msgs.append(f"{b_key} -> {ctl_key} : {short(t['name'], 60)}")
        for rule in split(t["rules"]):
            msgs.append(f"note right of {ctl_key} : {rule}: {short(m.ix['rules'][rule]['statement'], 60)}")
        for a in m.arcs_of(tid, c):
            p = m.ix["places"][a["place_id"]]
            if p["kind"] == "clock":
                continue
            if p["kind"] == "channel":
                f = m.ix["flows"][p["flow_id"]]
                if a["direction"] == "out":
                    to = f["to_id"]
                    e_key = pid("N_" + to)
                    part("participant", e_key, short(m.label(to), 30))
                    msgs.append(f"{ctl_key} -> {e_key} : {p['flow_id']} {short(p['name'], 60)}")
                continue
            h = m.holder(p["place_id"], c)
            held = h["held_in"] if h else ""
            e_key = pid("E_" + (held or p["place_id"]))
            part("entity", e_key, short(m.label(held), 30) if held else "record")
            verb = {"in": "use", "out": "write", "read": "read"}[a["direction"]]
            msgs.append(f"{ctl_key} -> {e_key} : {verb}: {short(p['name'], 60)}")
    for kind, key, label in parts:
        out.append(f"{kind} {pq(label)} as {key}")
    out += msgs + ["@enduml"]
    return "\n".join(out) + "\n"


def use_case_diagram(m, ucs, title):
    out = ["@startuml", f"title {title}", "left to right direction", "skinparam shadowing false", "skinparam defaultFontName Helvetica"]
    roles = {}
    for uc in ucs:
        for tid in split(uc["transitions"]):
            r = m.ix["transitions"][tid]["role_id"]
            roles.setdefault(r, set()).add(uc["use_case_id"])
    for r in roles:
        out.append(f'actor {pq(short(m.ix["roles"][r]["name"], 36))} as {pid(r)}')
    chains = []
    for uc in ucs:
        if uc["chain_id"] not in chains:
            chains.append(uc["chain_id"])
    for ch in chains:
        out.append(f'rectangle {pq(short(m.ix["chains"][ch]["name"], 70))} {{')
        for uc in ucs:
            if uc["chain_id"] == ch:
                out.append(f'  usecase {pq(uc["use_case_id"] + " " + uc["name"])} as {pid(uc["use_case_id"])}')
        out.append("}")
    for r, us in roles.items():
        for u in sorted(us):
            out.append(f"{pid(r)} -- {pid(u)}")
    out.append("@enduml")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ business use cases from the sequence diagrams

def business_use_case(m, did):
    seq = m.sequences[did]
    steps = {s["step_id"]: s for s in m.t["steps"] if s["diagram_id"] == did}
    lines = []

    def sentence(it):
        s = steps[f"{did}-{it['n']:02d}"]
        who = m.label(s["who_node"])
        if s["own_action"] == "yes":
            return f"{it['n']}. {who}: {s['text']}"
        return f"{it['n']}. {who} to {m.label(s['to_node'])}: {s['text']}"

    basic, alternates = [], []

    def walk(items, target, depth=0):
        for it in items:
            if it["type"] == "msg":
                target.append(sentence(it))
            elif it["type"] in ("alt", "critical"):
                first = it["branches"][0]
                target.append(f"(choice: {first['label']})")
                walk(first["items"], target, depth + 1)
                for br in it["branches"][1:]:
                    alt = [f"Instead, when: {br['label']}"]
                    walk(br["items"], alt, depth + 1)
                    alternates.append(alt)
            elif it["type"] == "opt":
                alt = [f"Only when: {it['branches'][0]['label']}"]
                walk(it["branches"][0]["items"], alt, depth + 1)
                alternates.append(alt)
            elif it["type"] == "par":
                target.append("(at the same time:)")
                for br in it["branches"]:
                    target.append(f"  ({br['label']})")
                    walk(br["items"], target, depth + 1)
            elif it["type"] == "loop":
                target.append(f"(repeated: {it['branches'][0]['label']})")
                walk(it["branches"][0]["items"], target, depth + 1)
            elif it["type"] != "note":
                for br in it.get("branches", []):
                    walk(br["items"], target, depth + 1)

    walk(seq["tree"]["items"], basic)
    actors = []
    for s in steps.values():
        for r in (s["who_role"], s["to_role"]):
            if r and r not in actors:
                actors.append(r)
    lines.append(f"### BUC-{did} {m.seq_title(did)}")
    lines.append("")
    lines.append(f"Source: atlas diagram {did} ({seq['file']}). Actors: " + ", ".join(m.ix["roles"][r]["name"] for r in actors) + ".")
    lines.append("")
    lines.append("Basic course:")
    lines.append("")
    for b in basic:
        lines.append(f"- {b}")
    if alternates:
        lines.append("")
        lines.append("Alternate courses:")
        lines.append("")
        for alt in alternates:
            lines.append(f"- {alt[0]}: " + " ".join(x for x in alt[1:]))
    lines.append("")
    return "\n".join(lines)
