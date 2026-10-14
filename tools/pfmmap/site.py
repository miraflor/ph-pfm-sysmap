"""Data for the interactive map, with the layouts computed by Graphviz, and the HTML page that shows it."""

import json
import re
import subprocess


def lw(text, width):
    """Label for a layout: quotes and backslashes removed, wrapped."""
    from . import maps as _m
    return _m.wrap(str(text).replace('"', "'").replace("\\", "/"), width)

from pathlib import Path

from . import maps, petri
from .model import cohorts_of, split


def _graphviz_json(dot_text, engine="dot"):
    res = subprocess.run([engine, "-Tjson"], input=dot_text.encode("utf-8"), check=True, capture_output=True, timeout=600)
    return json.loads(res.stdout)


def _positions(data):
    bb = [float(v) for v in data["bb"].split(",")]
    out = {}
    for o in data.get("objects", []):
        if "pos" in o and not o.get("name", "").startswith("cluster_"):
            x, y = (float(v) for v in o["pos"].split(","))
            out[o["name"]] = {"x": round(x, 1), "y": round(bb[3] - y, 1),
                              "w": round(float(o.get("width", 0.5)) * 72, 1), "h": round(float(o.get("height", 0.3)) * 72, 1)}
    return out


ZONES_TOP = ["INST-COA", "INST-DICT", "INST-DILG", "EXT-PUBLIC", "INST-CSC", "INST-DOJ", "INST-GCG"]
ZONES = [
    ["INST-CONGRESS", "INST-EXEC", "INST-DEPDEV", "INST-PFMC"],
    ["INST-DBM", "INST-PSDBM", "INST-GPPB"],
    ["INST-NGA", "INST-IMPL", "INST-GOCC", "INST-LGU", "INST-BLGF"],
    ["INST-GSB", "INST-RPS", "INST-PAYAGENT", "INST-AGDB", "INST-AAB", "INST-PCHC"],
    ["INST-BTR", "INST-BSP", "INST-DOF", "INST-BIR", "INST-BOC"],
    ["EXT-SUPPLIER", "EXT-EMPLOYEE", "EXT-BENEF", "EXT-DEALER", "EXT-TAXPAYER", "EXT-PAYER", "INST-SSF"],
]
LEAF = {1: (156, 46), 2: (138, 38), 0: (170, 54)}
PAD, HEAD, GAP = 14, 30, 14
L0_BOX = (168, 64)          # size of a box in the compact layout of level 0
L0_COLGAP, L0_ROWGAP, L0_TOPGAP = 44, 18, 80


def _pack(m, nid, row_limit):
    """Size of a node, the positions of its leaves and the boxes of the nodes inside it, all relative to its
    top-left corner. The children are packed in rows (shelf packing). A box is (centre x, centre y, width, height)."""
    kids = m.children.get(nid, [])
    lvl = int(m.node(nid)["level"])
    if not kids:
        w, h = LEAF[lvl]
        return w, h, {nid: (w / 2, h / 2)}, {}
    packed = [(k,) + _pack(m, k, 470 if lvl == 0 else 300) for k in kids]
    x, y, row_h, width = PAD, HEAD, 0, 0
    pos, boxes = {}, {}
    for k, w, h, inner, inner_boxes in packed:
        if x > PAD and x + w > row_limit:
            x = PAD
            y += row_h + GAP
            row_h = 0
        for leaf, (lx, ly) in inner.items():
            pos[leaf] = (x + lx, y + ly)
        for b, (bx, by, bw, bh) in inner_boxes.items():
            boxes[b] = (x + bx, y + by, bw, bh)
        x += w + GAP
        row_h = max(row_h, h)
        width = max(width, x - GAP + PAD)
    height = y + row_h + PAD
    boxes[nid] = (width / 2, height / 2, width, height)
    return width, height, pos, boxes


def map_layout(m):
    """Two layouts of the map.

    The full layout places every leaf, and gives every node that has children a box: the space that its contents
    take when it is open. Institutions are placed in zones that follow the subject: authority and budget on the
    left, the spending agency in the middle, banks, treasury and revenue on the right, parties outside government
    at the far right, and oversight and the public on top.

    The compact layout places the institutions only, in the same zones, so that level 0 can be read on one screen."""
    placed, boxes, sizes = {}, {}, {}
    for zone in [ZONES_TOP] + ZONES:
        for inst in zone:
            limit = 760 if inst in ("INST-DBM", "INST-NGA") else 520
            sizes[inst] = _pack(m, inst, limit)

    def put(inst, left, top):
        w, h, inner, inner_boxes = sizes[inst]
        for leaf, (lx, ly) in inner.items():
            placed[leaf] = (left + lx, top + ly)
        for b, (bx, by, bw, bh) in inner_boxes.items():
            boxes[b] = (left + bx, top + by, bw, bh)

    col_w = [max(sizes[i][0] for i in col) for col in ZONES]
    top_h = max(sizes[i][1] for i in ZONES_TOP)
    x = 0
    for inst in ZONES_TOP:
        put(inst, x, 0)
        x += sizes[inst][0] + 60
    y_start = top_h + 140
    x0 = 0
    for ci, col in enumerate(ZONES):
        y = y_start
        for inst in col:
            w, h = sizes[inst][0], sizes[inst][1]
            put(inst, x0 + (col_w[ci] - w) / 2, y)
            y += h + 70
        x0 += col_w[ci] + 130
    missing = [n["node_id"] for n in m.t["nodes"] if not m.children.get(n["node_id"]) and n["node_id"] not in placed]
    if missing:
        raise ValueError("nodes without a zone: " + ", ".join(missing))
    # compact layout of level 0
    W0, H0 = L0_BOX
    col_x = [i * (W0 + L0_COLGAP) + W0 / 2 for i in range(len(ZONES))]
    total_w = col_x[-1] + W0 / 2
    compact = {}
    step = (total_w - W0) / (len(ZONES_TOP) - 1)
    for k, inst in enumerate(ZONES_TOP):
        compact[inst] = (W0 / 2 + k * step, H0 / 2)
    heights = [len(c) * H0 + (len(c) - 1) * L0_ROWGAP for c in ZONES]
    for ci, col in enumerate(ZONES):
        top = H0 + L0_TOPGAP + (max(heights) - heights[ci]) / 2
        for j, inst in enumerate(col):
            compact[inst] = (col_x[ci], top + j * (H0 + L0_ROWGAP) + H0 / 2)
    level0 = {n["node_id"] for n in m.t["nodes"] if n["level"] == "0"}
    if set(compact) != level0:
        raise ValueError("institutions without a zone: " + ", ".join(sorted(level0 - set(compact))))
    r = lambda v: round(v, 1)
    return {"leaf": {k: {"x": r(v[0]), "y": r(v[1])} for k, v in placed.items()},
            "box": {k: {"x": r(v[0]), "y": r(v[1]), "w": r(v[2]), "h": r(v[3])} for k, v in boxes.items()},
            "compact": {k: {"x": r(v[0]), "y": r(v[1])} for k, v in compact.items()}}


def net_layout(m, net_places, net_trans, net_arcs, label_place, label_trans, rankdir="TB"):
    lines = ["digraph net {", f"graph [rankdir={rankdir} nodesep=0.3 ranksep=0.35]", 'node [fontname="Helvetica" fontsize=9]']
    for p in net_places:
        lines.append(f'"{p}" [shape=ellipse label="{lw(label_place[p], 24)}"]')
    for t in net_trans:
        lines.append(f'"{t}" [shape=box label="{lw(label_trans[t], 24)}"]')
    for s, t in net_arcs:
        lines.append(f'"{s}" -> "{t}"')
    lines.append("}")
    return _positions(_graphviz_json("\n".join(lines)))


def chain_payload(m, chain, cohort):
    net = petri.chain_net(m, chain, cohort)
    lp = {p["place_id"]: ((p["flow_id"] + ": ") if p["flow_id"] else "") + p["name"] for p in net["places"]}
    lt = {t["transition_id"]: t["transition_id"] + " " + t["name"] for t in net["transitions"]}
    arcs = []
    for a in net["arcs"]:
        arcs.append((a["place_id"], a["transition_id"]) if a["direction"] in ("in", "read") else (a["transition_id"], a["place_id"]))
    pos = net_layout(m, list(lp), list(lt), arcs, lp, lt)
    ana = petri.chain_analysis(net)
    return {
        "id": net["id"], "chain": chain or "CH-ALL", "cohort": cohort,
        "places": [{"id": p["place_id"], **pos[p["place_id"]]} for p in net["places"]],
        "transitions": [{"id": t["transition_id"], **pos[t["transition_id"]]} for t in net["transitions"]],
        "arcs": [{"t": a["transition_id"], "p": a["place_id"], "d": a["direction"], "w": a["weight"]} for a in net["arcs"]],
        "sources": ana["sources"], "sinks": ana["sinks"],
    }


def sequence_payload(m, did):
    net = petri.build_seq(m, did)
    snd = petri.soundness(net)
    lp = {p["id"]: p["name"] if p["name"] in ("start", "end") else "" for p in net.places}
    lt = {t["id"]: ("" if t["silent"] else t["name"]) for t in net.trans}
    lines = ["digraph seq {", "graph [rankdir=TB nodesep=0.25 ranksep=0.28]", 'node [fontname="Helvetica" fontsize=8]']
    for p in net.places:
        lines.append(f'"{p["id"]}" [shape=circle width=0.3 fixedsize=true label=""]')
    for t in net.trans:
        if t["silent"]:
            lines.append(f'"{t["id"]}" [shape=box width=0.2 height=0.2 fixedsize=true label=""]')
        else:
            lines.append(f'"{t["id"]}" [shape=box label="{lw(t["name"], 44)}"]')
    for a in net.arcs:
        lines.append(f'"{a["source"]}" -> "{a["target"]}"')
    lines.append("}")
    pos = _positions(_graphviz_json("\n".join(lines)))
    return {
        "id": did, "title": net.title, "start": net.start, "end": net.end, "sound": snd,
        "places": [{"id": p["id"], "name": lp[p["id"]], **pos[p["id"]]} for p in net.places],
        "transitions": [{"id": t["id"], "name": t["name"], "silent": t["silent"], "step": t["step"], **pos[t["id"]]} for t in net.trans],
        "arcs": [{"s": a["source"], "t": a["target"]} for a in net.arcs],
    }


def evidence_of(m, basis):
    e = m.evidence(basis)
    return {"codes": e["codes"], "best": e["best"], "gk": e["has_gk"]}


def _claim_reviews(root):
    import csv
    path = root / "audit" / "claim_reviews.csv"
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def build_data(m, as_of):
    lay = map_layout(m)
    nodes = []
    for n in m.t["nodes"]:
        d = dict(n)
        nid = n["node_id"]
        d["children"] = sorted(m.children.get(nid, []))
        d["ev"] = evidence_of(m, n["basis"])
        if nid in lay["leaf"]:
            d["x"], d["y"] = lay["leaf"][nid]["x"], lay["leaf"][nid]["y"]
        if nid in lay["box"]:
            b = lay["box"][nid]
            d["fx"], d["fy"], d["fw"], d["fh"] = b["x"], b["y"], b["w"], b["h"]
        if nid in lay["compact"]:
            d["x0"], d["y0"] = lay["compact"][nid]["x"], lay["compact"][nid]["y"]
        nodes.append(d)
    flows = []
    for f in m.t["flows"]:
        d = dict(f)
        d["ev"] = evidence_of(m, f["basis"])
        d["steps"] = [s["step_id"] for s in m.t["steps"] if f["flow_id"] in split(s["flows"])]
        d["places"] = [p["place_id"] for p in m.t["places"] if p["flow_id"] == f["flow_id"]]
        flows.append(d)
    fields = {}
    for fl in m.t["fields"]:
        fields.setdefault(fl["record_id"], []).append(fl)
    records = []
    for r in m.t["records"]:
        d = dict(r)
        d["fields"] = sorted(fields.get(r["record_id"], []), key=lambda x: int(x["order"]))
        records.append(d)
    chains = []
    for c in m.t["chains"]:
        for coh in ("P", "E", "B"):
            if m.transitions_of(c["chain_id"], coh):
                chains.append(chain_payload(m, c["chain_id"], coh))
    for coh in ("P", "E", "B"):
        chains.append(chain_payload(m, None, coh))
    seqs = [sequence_payload(m, did) for did in sorted(m.sequences)]
    data = {
        "as_of": as_of,
        "nodes": nodes, "flows": flows, "records": records, "links": m.t["record_links"],
        "steps": m.t["steps"], "roles": m.t["roles"], "sources": m.t["sources"], "gaps": m.t["gaps"],
        "cohorts": m.t["cohorts"], "chains_meta": m.t["chains"], "places": m.t["places"], "transitions": m.t["transitions"],
        "bindings": m.t["bindings"], "holders": m.t["place_holders"], "rules": m.t["rules"], "use_cases": m.t["use_cases"],
        "vocab": m.t["vocab"], "nets": chains, "sequences": seqs, "claim_reviews": _claim_reviews(m.root),
    }
    return data


def write_page(data, template_dir, out_path, scripts, standalone=True):
    """Assemble the single HTML page: style, markup, data and the application script.

    standalone=True writes a complete HTML document (for docs/index.html). standalone=False writes the content
    only, for a host that adds the document skeleton itself."""
    tpl = (template_dir / "template.html").read_text(encoding="utf-8")
    css = (template_dir / "style.css").read_text(encoding="utf-8")
    js = (template_dir / "app.js").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (tpl.replace("/*STYLE*/", css)
               .replace("<!--SCRIPTS-->", "\n".join(f'<script src="{s}"></script>' for s in scripts))
               .replace("/*DATA*/", "window.PFM = " + payload + ";")
               .replace("/*APP*/", js))
    if standalone:
        cut = page.index('<div class="app">')
        page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + page[:cut] + '</head>\n<body>\n' + page[cut:] + '</body>\n</html>\n')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    return len(page.encode("utf-8"))
