"""Load the registers of model/ into one object, with helpers that the other modules share."""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "model"
EXTRACT = ROOT / "atlas_extract"

TABLES = {
    "nodes": "node_id", "flows": "flow_id", "records": "record_id", "fields": None, "record_links": "link_id",
    "steps": "step_id", "actor_map": "atlas_actor", "roles": "role_id", "chains": "chain_id", "places": "place_id",
    "place_holders": None, "transitions": "transition_id", "arcs": None, "bindings": None, "rules": "rule_id",
    "cohorts": "cohort_id", "gaps": "gap_id", "sources": "code", "vocab": None, "use_cases": "use_case_id",
}
COHORTS = ["P", "E", "B"]
EVIDENCE_ORDER = ["record_instance", "law", "executive_issuance", "budget_law", "rule", "owner_statement", "plan",
                  "assessment", "vendor", "press", "inference", "general_knowledge"]


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def split(value, sep=";"):
    return [v.strip() for v in (value or "").split(sep) if v.strip()]


def cohorts_of(value):
    """'all' or 'P;E' -> list of cohort ids."""
    v = (value or "all").strip()
    return list(COHORTS) if v in ("", "all") else split(v)


class Model:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.t = {}
        self.ix = {}
        for name, key in TABLES.items():
            rows = read_csv(self.root / "model" / f"{name}.csv")
            self.t[name] = rows
            if key:
                self.ix[name] = {r[key]: r for r in rows}
        self.sequences = json.loads((self.root / "atlas_extract" / "atlas_sequences.json").read_text(encoding="utf-8"))
        self.diagram_index = {r["id"]: r for r in read_csv(self.root / "atlas_extract" / "atlas_diagram_index.csv")}
        self._codes = sorted(self.ix["sources"], key=len, reverse=True)
        self.children = {}
        for n in self.t["nodes"]:
            self.children.setdefault(n["parent_id"], []).append(n["node_id"])

    # ------------------------------------------------------------- nodes
    def node(self, nid):
        return self.ix["nodes"][nid]

    def ancestors(self, nid):
        out = []
        while nid:
            out.append(nid)
            nid = self.ix["nodes"][nid]["parent_id"]
        return out

    def at_level(self, nid, level):
        """The ancestor of nid at the given level (or nid itself if it is coarser)."""
        for a in reversed(self.ancestors(nid)):
            if int(self.ix["nodes"][a]["level"]) >= level:
                return a
        return nid

    def institution(self, nid):
        return self.ancestors(nid)[-1]

    def seq_title(self, did):
        """Title of a sequence diagram of the atlas, without its identifier in front."""
        t = re.sub(r"\s+", " ", self.sequences[did]["title"]).strip()
        return t[len(did):].strip() if t.startswith(did + " ") else t

    def label(self, nid):
        """Short name of a node. A module is named with its system, for example 'BTMS: 2 Payments'."""
        n = self.ix["nodes"][nid]
        if n["level"] == "2" and n["parent_id"]:
            return self.ix["nodes"][n["parent_id"]]["name"] + ": " + n["name"]
        return n["name"]

    # ------------------------------------------------------------- sources
    def codes_in(self, basis):
        """Source codes named in a free-text basis, longest match first. 'GK' is a code."""
        text = basis or ""
        found = []
        for code in self._codes:
            pattern = r"(?<![A-Za-z0-9-])" + re.escape(code) + r"(?![A-Za-z0-9-])"
            if re.search(pattern, text):
                found.append(code)
                text = re.sub(pattern, " ", text)
        return found

    def evidence(self, basis):
        """Strongest kind of source among the codes of a basis, and whether general knowledge is part of it."""
        codes = self.codes_in(basis)
        types = [self.ix["sources"][c]["type"] for c in codes]
        best = None
        for t in EVIDENCE_ORDER:
            if t in types:
                best = t
                break
        return {"codes": codes, "best": best or "none", "has_gk": "general_knowledge" in types or bool(re.search(r"\bGK\b", basis or ""))}

    # ------------------------------------------------------------- chains
    def arcs_of(self, tid, cohort=None):
        out = []
        for a in self.t["arcs"]:
            if a["transition_id"] != tid:
                continue
            if cohort and cohort not in cohorts_of(a["cohorts"]):
                continue
            out.append(a)
        return out

    def transitions_of(self, chain=None, cohort=None):
        out = []
        for t in self.t["transitions"]:
            if chain and t["chain_id"] != chain:
                continue
            if cohort and cohort not in cohorts_of(t["cohorts"]):
                continue
            out.append(t)
        return out

    def binding(self, tid, cohort):
        rows = [b for b in self.t["bindings"] if b["transition_id"] == tid]
        for b in rows:
            if b["cohort"] == cohort:
                return b
        for b in rows:
            if b["cohort"] == "all":
                return b
        return None

    def holder(self, pid, cohort):
        rows = [h for h in self.t["place_holders"] if h["place_id"] == pid]
        for h in rows:
            if h["cohort"] == cohort:
                return h
        for h in rows:
            if h["cohort"] == "all":
                return h
        return None

    def vocab(self, table, column):
        return {v["value"] for v in self.t["vocab"] if v["table"] == table and v["column"] == column}
