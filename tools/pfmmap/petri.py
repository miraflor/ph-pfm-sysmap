"""Petri nets: the curated chains of model/, and nets made from the sequence diagrams of the atlas.

Two kinds of net are produced.

1. Chain nets (curated). Places are states, balances, channels of flows and clocks; transitions are acts of a
   role in a body or system. A read arc means that the transition needs the token and leaves it. A chain net is
   drawn for each cohort (P, E, B) because some transitions and arcs exist only in some cohorts.

2. Sequence nets (generated). Each sequence diagram of the atlas becomes a workflow net with one start place and
   one end place. Messages and own actions become transitions in the order of the diagram. Blocks become:
   alt = exclusive choice, opt = choice with a silent skip, par = parallel split and join, loop = repeat or exit.
   These nets are block-structured, and the build checks their soundness by searching their state space.
"""

import itertools
import textwrap
from xml.sax.saxutils import escape

from .model import cohorts_of, split

LINE_FILL = {"authority": "#d6e4f7", "claim": "#d5ecd5", "cash": "#fde0c2", "records": "#e6e6e6"}
LINE_STROKE = {"authority": "#1f4e8c", "claim": "#2e6b2e", "cash": "#a35200", "records": "#555555"}


def wrap(text, width=22):
    return "\\n".join(textwrap.wrap(text, width)) or text


def q(s):
    return '"' + str(s).replace('"', '\\"') + '"'


# ===================================================================== chain nets

def chain_net(m, chain=None, cohort="P"):
    """Places, transitions and arcs of one chain (or of all chains when chain is None) for one cohort."""
    trans = m.transitions_of(chain, cohort)
    tids = {t["transition_id"] for t in trans}
    arcs = [a for a in m.t["arcs"] if a["transition_id"] in tids and cohort in cohorts_of(a["cohorts"])]
    pids = []
    for a in arcs:
        if a["place_id"] not in pids:
            pids.append(a["place_id"])
    places = [m.ix["places"][p] for p in pids]
    return {"id": f"{chain or 'CH-ALL'}-{cohort}", "chain": chain or "CH-ALL", "cohort": cohort, "places": places,
            "transitions": trans, "arcs": arcs}


def chain_analysis(net):
    """Source and sink places, and transitions that only read."""
    produced = {a["place_id"] for a in net["arcs"] if a["direction"] == "out"}
    consumed = {a["place_id"] for a in net["arcs"] if a["direction"] == "in"}
    read = {a["place_id"] for a in net["arcs"] if a["direction"] == "read"}
    sources = [p["place_id"] for p in net["places"] if p["place_id"] not in produced]
    sinks = [p["place_id"] for p in net["places"] if p["place_id"] not in consumed and p["place_id"] not in read]
    return {"sources": sources, "sinks": sinks}


def difference_windows(m, places, cohort):
    """For places that should hold equal amounts, the transitions that change one of them and not all of them."""
    out = []
    for t in m.transitions_of(None, cohort):
        change = {}
        for a in m.arcs_of(t["transition_id"], cohort):
            if a["place_id"] in places and a["direction"] in ("in", "out"):
                change[a["place_id"]] = change.get(a["place_id"], 0) + (1 if a["direction"] == "out" else -1)
        changed = {p for p, v in change.items() if v}
        live = [p for p in places if cohort in cohorts_of(m.ix["places"][p]["cohorts"])]
        if changed and changed != set(live):
            out.append((t["transition_id"], t["name"], sorted(changed)))
    return out


def chain_dot(m, net, title):
    lines = ["digraph net {", f'graph [rankdir=TB nodesep=0.3 ranksep=0.35 fontname="Helvetica" label={q(title)} labelloc=t fontsize=12]',
             'node [fontname="Helvetica" fontsize=9]', 'edge [arrowsize=0.6]']
    for p in net["places"]:
        fill = LINE_FILL.get(p["line"], "#ffffff")
        stroke = LINE_STROKE.get(p["line"], "#555555")
        style = "filled,dashed" if p["kind"] == "channel" else "filled"
        per = 2 if p["kind"] == "balance" else 1
        mark = " ●" if p["initial"] else ""
        label = (p["flow_id"] + ": " if p["flow_id"] else "") + p["name"]
        lines.append(f'{q(p["place_id"])} [shape=ellipse style="{style}" peripheries={per} fillcolor="{fill}" color="{stroke}" '
                     f'label={q(wrap(label, 24) + mark)} tooltip={q(p["place_id"])}]')
    for t in net["transitions"]:
        b = m.binding(t["transition_id"], net["cohort"])
        kind = b["controller_kind"] if b else ""
        fill = "#ffffff" if kind != "software" else "#eaeaea"
        lines.append(f'{q(t["transition_id"])} [shape=box style="filled" fillcolor="{fill}" penwidth=1.6 '
                     f'label={q(t["transition_id"] + "\\n" + wrap(t["name"], 24))} tooltip={q(m.ix["roles"][t["role_id"]]["name"])}]')
    for a in net["arcs"]:
        if a["direction"] == "in":
            lines.append(f'{q(a["place_id"])} -> {q(a["transition_id"])}' + (' [label="amount" fontsize=7]' if a["weight"] == "amount" else ""))
        elif a["direction"] == "out":
            lines.append(f'{q(a["transition_id"])} -> {q(a["place_id"])}')
        else:
            lines.append(f'{q(a["place_id"])} -> {q(a["transition_id"])} [style=dotted arrowhead=none color="#777777" label="read" fontsize=7]')
    lines.append("}")
    return "\n".join(lines)


def pnml(net_id, name, places, transitions, arcs):
    """Place/transition net in PNML. A read arc is written as two arcs (a self-loop)."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">',
           f'  <net id="{escape(net_id)}" type="http://www.pnml.org/version-2009/grammar/ptnet">',
           f'    <name><text>{escape(name)}</text></name>', '    <page id="page1">']
    for p in places:
        out.append(f'      <place id="{escape(p["id"])}"><name><text>{escape(p["name"])}</text></name>'
                   + (f'<initialMarking><text>{p["initial"]}</text></initialMarking>' if p.get("initial") else "") + '</place>')
    for t in transitions:
        out.append(f'      <transition id="{escape(t["id"])}"><name><text>{escape(t["name"])}</text></name></transition>')
    n = 0
    for a in arcs:
        pairs = [(a["source"], a["target"])]
        if a.get("read"):
            pairs = [(a["source"], a["target"]), (a["target"], a["source"])]
        for s, t in pairs:
            n += 1
            out.append(f'      <arc id="a{n}" source="{escape(s)}" target="{escape(t)}"/>')
    out += ["    </page>", "  </net>", "</pnml>"]
    return "\n".join(out) + "\n"


def chain_pnml(m, net, name):
    places = [{"id": p["place_id"], "name": p["name"], "initial": "1" if p["initial"] else ""} for p in net["places"]]
    trans = [{"id": t["transition_id"], "name": t["name"]} for t in net["transitions"]]
    arcs = []
    for a in net["arcs"]:
        if a["direction"] == "in":
            arcs.append({"source": a["place_id"], "target": a["transition_id"]})
        elif a["direction"] == "out":
            arcs.append({"source": a["transition_id"], "target": a["place_id"]})
        else:
            arcs.append({"source": a["place_id"], "target": a["transition_id"], "read": True})
    return pnml(net["id"], name, places, trans, arcs)


# ===================================================================== sequence nets

class SeqNet:
    def __init__(self, did, title):
        self.did = did
        self.title = title
        self.places = []
        self.trans = []
        self.arcs = []
        self.n = 0

    def place(self, label=""):
        self.n += 1
        pid = f"p{self.n}"
        self.places.append({"id": pid, "name": label or pid})
        return pid

    def transition(self, tid, name, silent=False, step=None):
        self.trans.append({"id": tid, "name": name, "silent": silent, "step": step})
        return tid

    def arc(self, s, t):
        self.arcs.append({"source": s, "target": t})


def build_seq(m, did):
    seq = m.sequences[did]
    steps = {s["step_id"]: s for s in m.t["steps"] if s["diagram_id"] == did}
    net = SeqNet(did, m.seq_title(did))
    start = net.place("start")
    net.places[-1]["initial"] = "1"
    counter = itertools.count(1)

    def label_of(item):
        sid = f"{did}-{item['n']:02d}"
        s = steps[sid]
        who = m.label(s["who_node"])
        to = "" if s["own_action"] == "yes" else " to " + m.label(s["to_node"])
        return sid, f"{item['n']}. {who}{to}: {s['text']}"

    def emit(items, p_in):
        cur = p_in
        for it in items:
            if it["type"] == "note":
                continue
            if it["type"] == "msg":
                sid, lab = label_of(it)
                t = net.transition(f"t{it['n']:02d}", lab, step=sid)
                net.arc(cur, t)
                nxt = net.place()
                net.arc(t, nxt)
                cur = nxt
                continue
            kind = it["type"]
            branches = it["branches"]
            out = net.place()
            if kind in ("alt", "critical"):
                for br in branches:
                    if not any(x["type"] == "msg" for x in br["items"]):
                        k = next(counter)
                        t = net.transition(f"tau{k}", f"silent: {br['label']}", silent=True)
                        net.arc(cur, t)
                        net.arc(t, out)
                        continue
                    end = emit(br["items"], cur)
                    k = next(counter)
                    t = net.transition(f"tau{k}", f"end of: {br['label']}", silent=True)
                    net.arc(end, t)
                    net.arc(t, out)
            elif kind == "opt":
                k = next(counter)
                skip = net.transition(f"tau{k}", f"skip: {branches[0]['label']}", silent=True)
                net.arc(cur, skip)
                net.arc(skip, out)
                end = emit(branches[0]["items"], cur)
                k = next(counter)
                t = net.transition(f"tau{k}", f"end of: {branches[0]['label']}", silent=True)
                net.arc(end, t)
                net.arc(t, out)
            elif kind == "par":
                k = next(counter)
                split_t = net.transition(f"tau{k}", "parallel split", silent=True)
                net.arc(cur, split_t)
                k = next(counter)
                join_t = net.transition(f"tau{k}", "parallel join", silent=True)
                for br in branches:
                    b_in = net.place()
                    net.arc(split_t, b_in)
                    end = emit(br["items"], b_in)
                    net.arc(end, join_t)
                net.arc(join_t, out)
            elif kind == "loop":
                body_in = net.place()
                k = next(counter)
                enter = net.transition(f"tau{k}", f"enter: {branches[0]['label']}", silent=True)
                net.arc(cur, enter)
                net.arc(enter, body_in)
                end = emit(branches[0]["items"], body_in)
                k = next(counter)
                redo = net.transition(f"tau{k}", "repeat", silent=True)
                net.arc(end, redo)
                net.arc(redo, body_in)
                k = next(counter)
                exit_t = net.transition(f"tau{k}", "exit the loop", silent=True)
                net.arc(end, exit_t)
                net.arc(exit_t, out)
            else:  # rect, break and other blocks: in sequence
                end = emit(branches[0]["items"], cur)
                k = next(counter)
                t = net.transition(f"tau{k}", f"end of block {kind}", silent=True)
                net.arc(end, t)
                net.arc(t, out)
            cur = out
        return cur

    last = emit(seq["tree"]["items"], start)
    net.places[[p["id"] for p in net.places].index(last)]["name"] = "end"
    net.start, net.end = start, last
    return net


def soundness(net, limit=200000):
    """State space search of a 1-safe workflow net: option to complete, proper completion, no dead transition."""
    pre = {t["id"]: [] for t in net.trans}
    post = {t["id"]: [] for t in net.trans}
    for a in net.arcs:
        if a["source"] in pre:
            post[a["source"]].append(a["target"])
        else:
            pre[a["target"]].append(a["source"])
    init = frozenset([net.start])
    seen = {init}
    edges = {}
    stack = [init]
    fired = set()
    unsafe = False
    while stack:
        mk = stack.pop()
        succ = []
        for t in net.trans:
            if all(p in mk for p in pre[t["id"]]):
                new = set(mk) - set(pre[t["id"]])
                for p in post[t["id"]]:
                    if p in new:
                        unsafe = True
                    new.add(p)
                new = frozenset(new)
                fired.add(t["id"])
                succ.append(new)
                if new not in seen:
                    seen.add(new)
                    stack.append(new)
                    if len(seen) > limit:
                        return {"checked": False, "reason": "state space too large"}
        edges[mk] = succ
    final = frozenset([net.end])
    # markings that can reach the final marking
    rev = {}
    for a, bs in edges.items():
        for b in bs:
            rev.setdefault(b, set()).add(a)
    good = {final} if final in seen else set()
    frontier = list(good)
    while frontier:
        x = frontier.pop()
        for y in rev.get(x, ()):
            if y not in good:
                good.add(y)
                frontier.append(y)
    option = all(mk in good for mk in seen)
    proper = all(not (net.end in mk and mk != final) for mk in seen)
    dead = [t["id"] for t in net.trans if t["id"] not in fired]
    return {"checked": True, "states": len(seen), "option_to_complete": option, "proper_completion": proper,
            "dead_transitions": dead, "safe": not unsafe, "sound": option and proper and not dead and not unsafe}


def seq_dot(net):
    lines = ["digraph seq {", f'graph [rankdir=TB nodesep=0.25 ranksep=0.3 fontname="Helvetica" label={q(net.did + "  " + net.title)} labelloc=t fontsize=11]',
             'node [fontname="Helvetica" fontsize=8]', 'edge [arrowsize=0.5]']
    for p in net.places:
        lab = p["name"] if p["name"] in ("start", "end") else ""
        lines.append(f'{q(p["id"])} [shape=circle width=0.25 fixedsize=true label={q(lab)} fontsize=6 style=filled fillcolor="{"#333333" if p.get("initial") else "#ffffff"}"]')
    for t in net.trans:
        if t["silent"]:
            lines.append(f'{q(t["id"])} [shape=box width=0.15 height=0.15 style=filled fillcolor="#444444" label="" tooltip={q(t["name"])}]')
        else:
            lines.append(f'{q(t["id"])} [shape=box style=rounded label={q(wrap(t["name"], 46))} tooltip={q(t["step"])}]')
    for a in net.arcs:
        lines.append(f'{q(a["source"])} -> {q(a["target"])}')
    lines.append("}")
    return "\n".join(lines)
