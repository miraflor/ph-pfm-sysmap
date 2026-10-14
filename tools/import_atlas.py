"""Extract the content of the Philippine PFM Atlas into plain tables.

The map in this repository does not need the atlas at build time. This script
was used once to take the first copy of the atlas content, and it can be run
again to compare a newer atlas with the copy in atlas_extract/.

Usage:
    python tools/import_atlas.py PATH_TO_ATLAS_CLONE [--out atlas_extract]

It reads only files of the atlas and writes only into the output folder.
"""

import argparse
import csv
import json
import re
import shutil
from pathlib import Path


def clean(text):
    """Remove Mermaid line breaks and markup from a label."""
    text = text.replace("<br/>", " ").replace("<br>", " ").replace("#nbsp;", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def md_tables(path):
    """Return every Markdown table of a file with the heading above it."""
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    out, section, i = [], "", 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#"):
            section = line.lstrip("#").strip()
        if (
            line.strip().startswith("|")
            and i + 1 < len(lines)
            and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1])
        ):
            header = split_row(line)
            rows, j = [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            out.append({"section": section, "header": header, "rows": rows, "line": i + 1})
            i = j
            continue
        i += 1
    return out


def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def strip_md(text):
    """Remove bold marks of Markdown, keep the words."""
    return text.replace("**", "").strip()


# ---------------------------------------------------------------- Mermaid parsers

MSG = re.compile(r"^([A-Za-z0-9_]+)\s*(-->>|->>|-->|->|--x|-x|--\)|-\))\s*[+-]?([A-Za-z0-9_]+)\s*:\s*(.*)$")
PART = re.compile(r"^(participant|actor)\s+([A-Za-z0-9_]+)(?:\s+as\s+(.*))?$")
BLOCK_OPEN = re.compile(r"^(alt|opt|par|loop|critical|break|rect)\b\s*(.*)$")
BLOCK_NEXT = re.compile(r"^(else|and|option)\b\s*(.*)$")
NOTE = re.compile(r"^Note\s+(over|left of|right of)\s+([^:]+):\s*(.*)$", re.I)


def parse_sequence(path):
    """Parse a Mermaid sequence diagram into participants and a block tree.

    Each message receives the number that Mermaid's autonumber gives it, so
    that it can be matched with the steps register of the atlas.
    """
    text = Path(path).read_text(encoding="utf-8")
    title = ""
    m = re.search(r'title:\s*"(.*)"', text)
    if m:
        title = m.group(1)
    participants = {}
    root = {"type": "seq", "items": []}
    stack = [root]
    branch_stack = []
    counter = 0
    for raw in text.split("\n"):
        line = raw.strip()
        if not line or line.startswith("%%") or line in ("---", "sequenceDiagram", "autonumber"):
            continue
        if line.startswith("title:") or line.startswith("config:"):
            continue
        p = PART.match(line)
        if p:
            participants[p.group(2)] = clean(p.group(3) or p.group(2))
            continue
        n = NOTE.match(line)
        if n:
            stack[-1]["items"].append({"type": "note", "over": n.group(2).strip(), "text": clean(n.group(3))})
            continue
        b = BLOCK_OPEN.match(line)
        if b:
            block = {"type": b.group(1), "branches": [{"label": clean(b.group(2)), "items": []}]}
            stack[-1]["items"].append(block)
            branch_stack.append(block)
            stack.append(block["branches"][0])
            continue
        b2 = BLOCK_NEXT.match(line)
        if b2 and branch_stack:
            stack.pop()
            block = branch_stack[-1]
            br = {"label": clean(b2.group(2)), "items": []}
            block["branches"].append(br)
            stack.append(br)
            continue
        if line == "end" and branch_stack:
            stack.pop()
            branch_stack.pop()
            continue
        mm = MSG.match(line)
        if mm:
            counter += 1
            stack[-1]["items"].append(
                {
                    "type": "msg",
                    "n": counter,
                    "from": mm.group(1),
                    "to": mm.group(3),
                    "arrow": mm.group(2),
                    "text": clean(mm.group(4)),
                }
            )
            continue
    return {"title": title, "participants": participants, "tree": root, "messages": counter}


ENTITY = re.compile(r"^([A-Z_][A-Z0-9_]*)\s*\{\s*$")
FIELD = re.compile(r'^(\w+)\s+(\w+)(?:\s+(PK|FK))?(?:\s+"(.*)")?\s*$')
REL = re.compile(r'^([A-Z_][A-Z0-9_]*)\s+(\S+)\s+([A-Z_][A-Z0-9_]*)\s*:\s*"(.*)"\s*$')


def parse_er(path):
    entities, relations, current = {}, [], None
    for raw in Path(path).read_text(encoding="utf-8").split("\n"):
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        e = ENTITY.match(line)
        if e:
            current = e.group(1)
            entities[current] = []
            continue
        if line == "}":
            current = None
            continue
        if current:
            f = FIELD.match(line)
            if f:
                entities[current].append(
                    {"type": f.group(1), "name": f.group(2), "key": f.group(3) or "", "note": f.group(4) or ""}
                )
            continue
        r = REL.match(line)
        if r:
            relations.append({"from": r.group(1), "card": r.group(2), "to": r.group(3), "label": r.group(4)})
    return {"entities": entities, "relations": relations}


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("atlas")
    ap.add_argument("--out", default="atlas_extract")
    args = ap.parse_args()
    atlas = Path(args.atlas)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ref = atlas / "src" / "reference"

    # Reference B: systems in use and planned
    for t in md_tables(ref / "B_information_systems_inventory.md"):
        if t["section"].startswith("2. Systems in use"):
            write_csv(out / "atlas_systems_in_use.csv", ["system", "owner", "user", "recipient", "what_it_holds_or_does", "basis"],
                      [[strip_md(c) for c in r] for r in t["rows"]])
        if t["section"].startswith("3. Systems that are planned"):
            write_csv(out / "atlas_systems_planned.csv", ["system", "lead", "plan", "basis"],
                      [[strip_md(c) for c in r] for r in t["rows"]])

    # Register of interfaces (built CSV of the atlas)
    shutil.copy(atlas / "docs" / "atlas" / "reference" / "interface_register.csv", out / "atlas_flows.csv")
    shutil.copy(atlas / "docs" / "atlas" / "reference" / "steps_register.csv", out / "atlas_steps.csv")
    shutil.copy(atlas / "docs" / "atlas" / "reference" / "diagram_index.csv", out / "atlas_diagram_index.csv")

    # Research registers
    reg = out / "research_registers"
    reg.mkdir(exist_ok=True)
    for f in (atlas / "research_models" / "registers").glob("*.csv"):
        shutil.copy(f, reg / f.name)

    # Reference F: sources
    rows = []
    for t in md_tables(ref / "F_sources_and_verification.md"):
        if t["section"].startswith("2.") and t["header"][:2] == ["Code", "Source"]:
            for r in t["rows"]:
                rows.append([r[0], r[1], r[2] if len(r) > 2 else "", r[3] if len(r) > 3 else "", t["section"]])
    write_csv(out / "atlas_sources.csv", ["code", "source", "how_read", "used_for", "section"], rows)
    for t in md_tables(ref / "F_sources_and_verification.md"):
        if t["section"].startswith("4."):
            write_csv(out / "atlas_documents_not_opened.csv", ["document", "governs", "chapters_affected"], t["rows"])

    # Reference G: open points
    rows = []
    for t in md_tables(ref / "G_open_questions_and_known_gaps.md"):
        if t["section"].startswith("1.") or t["section"].startswith("2."):
            h = t["header"]
            for r in t["rows"]:
                rec = dict(zip(h, r))
                rows.append([
                    rec.get("No.", ""),
                    t["section"],
                    strip_md(rec.get("Subject", rec.get("Open point", ""))),
                    rec.get("Source A", rec.get("Text A", rec.get("Why it matters", ""))),
                    rec.get("Source B", rec.get("Text B", "")),
                    rec.get("What the atlas does", rec.get("Where to check", "")),
                ])
    write_csv(out / "atlas_open_points.csv", ["no", "section", "subject_or_point", "a_or_why", "b", "atlas_action_or_where_to_check"], rows)

    # Reference C: documents, links, proofs
    docs, links, proves = [], [], []
    for t in md_tables(ref / "C_documents_and_identifiers.md"):
        if t["header"][0] == "Document":
            for r in t["rows"]:
                docs.append([strip_md(c) for c in r] + [t["section"]])
        elif t["section"].startswith("10."):
            links = t["rows"]
        elif t["section"].startswith("11."):
            proves = t["rows"]
    write_csv(out / "atlas_documents.csv", ["document", "issued_by", "what_it_does", "identified_by", "basis", "section"], docs)
    write_csv(out / "atlas_record_links.csv", ["no", "from_record", "to_record", "linking_key", "kind_of_key", "field_read"], links)
    write_csv(out / "atlas_what_records_prove.csv", ["no", "record", "proves", "does_not_prove", "basis"], proves)

    # Reference A: authorities
    rows = []
    for t in md_tables(ref / "A_authorities_and_mandates.md"):
        h = t["header"]
        for r in t["rows"]:
            rec = dict(zip(h, r))
            rows.append([strip_md(rec.get("Authority", rec.get("Party", ""))), rec.get("Role in PFM", ""),
                         rec.get("Systems it owns", ""), rec.get("Chapters", ""), rec.get("Basis", ""), t["section"]])
    write_csv(out / "atlas_authorities.csv", ["authority", "role_in_pfm", "systems_it_owns", "chapters", "basis", "section"], rows)

    # Mermaid sequence diagrams and the data model of 17c
    seqs = {}
    for f in sorted((atlas / "src" / "diagrams" / "mermaid").glob("*.mmd")):
        head = f.read_text(encoding="utf-8")
        if "sequenceDiagram" in head:
            seqs[f.name.split("_")[0]] = dict(parse_sequence(f), file=f.name)
    (out / "atlas_sequences.json").write_text(json.dumps(seqs, indent=1, ensure_ascii=False), encoding="utf-8")
    er = parse_er(atlas / "src" / "diagrams" / "mermaid" / "17c_record_lineage_er.mmd")
    (out / "atlas_er_17c.json").write_text(json.dumps(er, indent=1, ensure_ascii=False), encoding="utf-8")

    # Check: number of messages per sequence equals the number of steps in the register
    steps = list(csv.DictReader(open(out / "atlas_steps.csv", encoding="utf-8-sig")))
    count = {}
    for s in steps:
        count[s["diagram_id"]] = count.get(s["diagram_id"], 0) + 1
    report = []
    for k, v in seqs.items():
        report.append(f"{k}: {v['messages']} messages in the diagram, {count.get(k, 0)} steps in the register")
    (out / "IMPORT_REPORT.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
