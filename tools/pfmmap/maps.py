"""Graphviz maps of the systems at three levels, and the layout used by the interactive map."""

import json
import subprocess
import textwrap

from .model import cohorts_of, split

GROUP_FILL = {
    "budget": "#dde9f7", "procurement": "#e2f0d6", "finance": "#f7ecd2", "treasury": "#fbe0c4", "revenue": "#f6dfe8",
    "local": "#d8f0e6", "audit": "#e6e3fb", "planning": "#ece9df", "ict": "#dceff3", "banking": "#fdf0d5",
    "spending": "#eef6e6", "political": "#eeeeee", "oversight": "#eeeeee", "governance": "#efefef", "other": "#f2f2f2",
    "external": "#ffffff",
}
KIND_COLOR = {"authority": "#1f4e8c", "document": "#2e6b2e", "money": "#a35200", "data": "#555555"}
MEDIUM_STYLE = {
    "paper": "dotted", "data_entry": "dashed", "download": "dashed", "own_register": "dashed", "electronic_unspecified": "solid", "api": "bold",
    "payment_network": "bold", "bank_transfer": "solid", "cash_or_check": "solid", "public_website": "solid", "not_stated": "solid",
}
STAGE_ALPHA = {"in_use": "", "in_use_part": "", "described_not_verified": "99", "planned": "66", "not_stated": "bb"}
SHAPE = {"institution": "box", "external": "box", "unit": "box", "system": "box", "module": "box", "account": "cylinder",
         "network": "hexagon", "standard": "note", "website": "tab"}


def wrap(text, width=20):
    return "\\n".join(textwrap.wrap(text, width)) or text


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\\\\n", "\\n") + '"'


def node_attrs(m, n, collapsed=False):
    style = ["filled"]
    if n["type"] in ("system", "module", "institution", "external"):
        style.append("rounded")
    if n["status"] == "planned":
        style.append("dashed")
    elif n["status"] in ("retiring", "not_stated"):
        style.append("dotted")
    fill = GROUP_FILL.get(n["group"], "#ffffff")
    if n["type"] in ("unit",):
        fill = "#ffffff"
    pen = "1.6" if collapsed or n["level"] == "0" else "1"
    label = wrap(n["name"], 18 if n["level"] != "2" else 16)
    font = "Helvetica-Bold" if (collapsed or n["level"] == "0") else "Helvetica"
    color = "#888888" if n["status"] in ("described_not_verified", "required_by_law") else "#333333"
    return (f'shape={SHAPE.get(n["type"], "box")} style="{",".join(style)}" fillcolor="{fill}" color="{color}" '
            f'penwidth={pen} fontname="{font}" fontsize={9 if n["level"] == "2" else 10} label={q(label)} '
            f'tooltip={q(n["full_name"])}')


def flow_edge_attrs(f, label=True):
    color = KIND_COLOR[f["kind"]] + STAGE_ALPHA.get(f["stage"], "")
    style = MEDIUM_STYLE.get(f["medium"], "solid")
    width = "1.8" if f["medium"] in ("api", "payment_network") else ("1.3" if f["kind"] == "money" else "1")
    arrow = "empty" if f["stage"] == "planned" else "normal"
    lab = f' label={q(f["flow_id"])} fontsize=7 fontcolor="#666666"' if label else ""
    return f'color="{color}" style="{style}" penwidth={width} arrowhead={arrow} arrowsize=0.6 tooltip={q(f["flow_id"] + ": " + f["what_passes"])}{lab}'


def visible_flows(m, include_planned=True, include_adjacent=False, domains=None):
    out = []
    for f in m.t["flows"]:
        if not include_planned and f["stage"] == "planned":
            continue
        if domains and f["domain"] not in domains:
            continue
        ends = [f["from_id"], f["to_id"]] + ([f["via_id"]] if f["via_id"] else [])
        if not include_adjacent and any(m.node(e)["scope"] == "adjacent" for e in ends):
            continue
        out.append(f)
    return out


def segments(f):
    if f["via_id"]:
        return [(f["from_id"], f["via_id"]), (f["via_id"], f["to_id"])]
    return [(f["from_id"], f["to_id"])]


def dot_level0(m, flows):
    lines = ['digraph L0 {', 'graph [rankdir=LR newrank=true nodesep=0.35 ranksep=0.9 fontname="Helvetica" splines=spline '
             'label="Level 0. Institutions and parties. A line joins two bodies when at least one flow passes between their systems or units; the number is the count of flows." '
             'labelloc=t fontsize=12 tooltip="Level 0"]', 'node [margin="0.12,0.06"]', 'edge [fontname="Helvetica"]']
    agg = {}
    for f in flows:
        for a, b in segments(f):
            A, B = m.institution(a), m.institution(b)
            if A == B:
                continue
            agg.setdefault((A, B), []).append(f)
    used = {x for k in agg for x in k}
    for nid in sorted(used):
        lines.append(f'{q(nid)} [{node_attrs(m, m.node(nid), collapsed=True)}]')
    for (a, b), fs in sorted(agg.items()):
        kinds = sorted({f["kind"] for f in fs})
        color = KIND_COLOR[kinds[0]] if len(kinds) == 1 else "#444444"
        lines.append(f'{q(a)} -> {q(b)} [label={q(len(fs))} fontsize=8 color="{color}" penwidth={min(0.8 + 0.35 * len(fs), 4):.1f} '
                     f'arrowsize=0.6 tooltip={q("; ".join(f["flow_id"] + " " + f["what_passes"][:60] for f in fs))}]')
    lines.append("}")
    return "\n".join(lines), agg


def dot_detail(m, flows, level, title, name="L1"):
    """Level 1 or 2: nodes at that level inside clusters of their parents; one edge per flow."""
    ends = set()
    for f in flows:
        for a, b in segments(f):
            ends.add(m.at_level(a, level))
            ends.add(m.at_level(b, level))
    lines = [f'digraph {name} {{', f'graph [rankdir=LR newrank=true compound=true nodesep=0.25 ranksep=0.7 fontname="Helvetica" splines=spline '
             f'label={q(title)} labelloc=t fontsize=12]', 'node [margin="0.08,0.04"]', 'edge [fontname="Helvetica"]']
    # group the visible nodes by institution, and by system for level 2
    by_inst = {}
    for nid in ends:
        by_inst.setdefault(m.institution(nid), []).append(nid)
    for inst, members in sorted(by_inst.items()):
        n0 = m.node(inst)
        inner = [x for x in members if x != inst]
        if not inner:
            lines.append(f'{q(inst)} [{node_attrs(m, n0, collapsed=True)}]')
            continue
        lines.append(f'subgraph {q("cluster_" + inst)} {{')
        lines.append(f'label={q(wrap(n0["name"], 30))} style="rounded,filled" fillcolor="{GROUP_FILL.get(n0["group"], "#ffffff")}" '
                     f'color="#999999" fontname="Helvetica-Bold" fontsize=10 tooltip={q(n0["full_name"])}')
        if inst in members:
            lines.append(f'{q(inst)} [{node_attrs(m, n0)} label={q(wrap(n0["name"] + " (as a whole)", 18))} fillcolor="#ffffff"]')
        if level == 2:
            by_sys = {}
            for x in inner:
                anc = m.ancestors(x)
                key = anc[-2] if len(anc) >= 2 else x
                by_sys.setdefault(key, []).append(x)
            for sysid, mods in sorted(by_sys.items()):
                mods_only = [x for x in mods if x != sysid]
                if mods_only:
                    s = m.node(sysid)
                    lines.append(f'subgraph {q("cluster_" + sysid)} {{')
                    lines.append(f'label={q(wrap(s["name"], 24))} style="rounded,filled" fillcolor="#ffffff" color="#777777" fontname="Helvetica-Bold" fontsize=9')
                    if sysid in mods:
                        lines.append(f'{q(sysid)} [{node_attrs(m, s)} label={q(wrap(s["name"] + " (as a whole)", 16))}]')
                    for x in sorted(mods_only):
                        lines.append(f'{q(x)} [{node_attrs(m, m.node(x))}]')
                    lines.append("}")
                else:
                    for x in mods:
                        lines.append(f'{q(x)} [{node_attrs(m, m.node(x))}]')
        else:
            for x in sorted(inner):
                lines.append(f'{q(x)} [{node_attrs(m, m.node(x))}]')
        lines.append("}")
    for f in flows:
        for a, b in segments(f):
            A, B = m.at_level(a, level), m.at_level(b, level)
            if A == B:
                continue
            lines.append(f'{q(A)} -> {q(B)} [{flow_edge_attrs(f)}]')
    lines.append("}")
    return "\n".join(lines)


def legend_dot():
    rows = []
    for k, c in KIND_COLOR.items():
        rows.append(f'<tr><td><font color="{c}">&#9472;&#9472;&#9472;</font></td><td align="left">{k}</td></tr>')
    styles = [("paper", "dotted: paper"), ("data_entry", "dashed: a person enters or uploads"), ("api", "bold: program to program"),
              ("not_stated", "thin: kind not stated")]
    for _, t in styles:
        rows.append(f'<tr><td></td><td align="left">{t}</td></tr>')
    return "".join(rows)


def render(dot_text, out_svg, engine="dot"):
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    dot_path = out_svg.with_suffix(".dot")
    dot_path.write_text(dot_text, encoding="utf-8")
    try:
        subprocess.run([engine, "-Tsvg", str(dot_path), "-o", str(out_svg)], check=True, capture_output=True, timeout=300)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print("  graphviz failed for", out_svg.name, getattr(e, "stderr", b"")[:300])
        return False


def layout_positions(dot_text, engine="dot"):
    """Run Graphviz and return {node: (x, y)} in points, y pointing down, for the interactive map."""
    try:
        res = subprocess.run([engine, "-Tjson"], input=dot_text.encode("utf-8"), check=True, capture_output=True, timeout=300)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return {}
    data = json.loads(res.stdout)
    bb = [float(v) for v in data["bb"].split(",")]
    pos = {}
    for o in data.get("objects", []):
        if "pos" in o and "nodes" not in o and not o.get("name", "").startswith("cluster_"):
            x, y = (float(v) for v in o["pos"].split(","))
            pos[o["name"]] = (round(x, 1), round(bb[3] - y, 1))
    return pos
