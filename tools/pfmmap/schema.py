"""Description of every register of model/ and of every column. The build writes docs/DATA_MODEL.md from it."""

ORDER = ["nodes", "flows", "records", "fields", "record_links", "steps", "actor_map", "roles", "chains", "places", "place_holders",
         "transitions", "arcs", "bindings", "rules", "use_cases", "cohorts", "gaps", "sources", "vocab"]

TABLES = {
    "nodes": ("The boxes of the map: institutions and parties (level 0), systems, accounts, networks, standards, websites and units (level 1), and modules (level 2). Every box has one parent, except the boxes of level 0.", {
        "node_id": "Identifier. INST- for an institution, EXT- for a party outside government, SYS- for a system or a website, MOD- for a module, ACC- for an account, NET- for a network, STD- for a standard, UNIT- for a unit.",
        "level": "0, 1 or 2.",
        "type": "Kind of box.",
        "parent_id": "The box that contains this one. Empty at level 0.",
        "name": "Short name, as drawn in the map.",
        "full_name": "Full name.",
        "group": "Part of PFM, used for the colour of the box: budget, procurement, treasury, revenue, banking, spending, audit, local, planning, ict, political, oversight, governance, finance, external, other.",
        "status": "Stage of use of a system (empty for institutions and units).",
        "scope": "core for public financial management; adjacent for a system next to it (shown only when you ask for it).",
        "owner": "Body that owns or runs the system.",
        "users": "Who enters the data.",
        "recipients": "Who reads the data.",
        "description": "What it is and does, in a few sentences. Source codes in square brackets.",
        "basis": "Source codes for the row (see sources.csv).",
        "atlas_ref": "Where the atlas describes it.",
        "since": "Year or month from which it is in use, when a source states it.",
        "note": "Anything a reader should know before using the row.",
    }),
    "flows": ("What passes from one box to another: data, a document, an authority or money. The 69 rows of the register of interfaces of the atlas (its Reference B) are all here; a few are split in two or three, and new rows have no atlas row.", {
        "flow_id": "Identifier. F and the number of the atlas row (F032); a letter is added when a row is split (F021A); numbers above 100 are new.",
        "atlas_row": "Number of the row in the register of the atlas. Empty for a new row.",
        "side": "Side of the atlas register: spending, revenue and treasury, inside one agency, or new.",
        "domain": "Part of PFM, used by the filters.",
        "from_id": "Box that sends.",
        "via_id": "Box the flow passes through, when the source names one (for example the servicing bank between BTMS and the clearing house).",
        "to_id": "Box that receives.",
        "what_passes": "What passes, in words.",
        "payload": "Records that pass (see records.csv), separated by semicolons.",
        "kind": "data, document, authority or money.",
        "agent": "Who moves the content. The atlas has one word, the carrier; here it is split into two questions, agent and medium.",
        "medium": "How the content passes.",
        "atlas_carrier": "The carrier of the atlas, as written there.",
        "stage": "Stage of use.",
        "cohorts": "Cohorts in which the flow exists (P, E, B, or all).",
        "timing": "When or how often it passes, when a source states it.",
        "standard": "Message standard, when a source states it.",
        "check": "How the two sides check each other, as in the atlas.",
        "basis": "Source codes for the row.",
        "gaps": "Open questions about the row (see gaps.csv).",
        "note": "Anything a reader should know before using the row.",
        "atlas_from": "The sender as written in the atlas.",
        "atlas_to": "The receiver as written in the atlas.",
    }),
    "records": ("The documents, reports, registers, authorities, data and money that the flows carry and the nets hold.", {
        "record_id": "Identifier, R- and a short name (R-LDDAP).",
        "name": "Name of the record, with its form number when it has one.",
        "kind": "Kind of record.",
        "issuer": "Who issues or signs it.",
        "issuer_node": "Box of the issuer.",
        "purpose": "What it is for.",
        "identified_by": "How one record is told apart from another (its number).",
        "form_ref": "Appendix of the Government Accounting Manual or other form number.",
        "basis": "Source codes for the row.",
        "atlas_ref": "Where the atlas describes it.",
        "note": "Anything a reader should know.",
    }),
    "fields": ("Fields of the records, from diagram 17c of the atlas (its entity diagram).", {
        "record_id": "Record that has the field.",
        "order": "Order of the field in the record.",
        "field": "Name of the field.",
        "type": "string, code, money, text or date.",
        "key": "PK for the field that identifies the record, FK for a field that points to another record, empty otherwise.",
        "references": "For an FK, the record it points to.",
        "note": "Note of the atlas on the field.",
        "basis": "Source codes; GK when the atlas marks it as general knowledge.",
        "atlas_ref": "Where the atlas has it.",
    }),
    "record_links": ("Links between records, from diagram 17c of the atlas.", {
        "link_id": "Identifier.",
        "from_record": "Record on the side of one.",
        "to_record": "Record on the side of many.",
        "relation": "Verb of the link, as in the atlas.",
        "key": "Field that carries the link. Empty when the source does not state it.",
        "cardinality": "Cardinality in the notation of Mermaid entity diagrams (||--o{ is one to zero or more).",
        "basis": "Diagram 17c, or GK when the atlas marks the link as general knowledge.",
        "atlas_ref": "Where the atlas has it.",
    }),
    "steps": ("Every message and own action of the twenty sequence diagrams of the atlas, one row each, in the order of the diagram.", {
        "step_id": "Diagram and number of the step (07a-05).",
        "diagram_id": "Diagram of the atlas.",
        "step": "Number of the step in the diagram.",
        "section": "Note of the diagram that comes before the step, when there is one.",
        "block": "Block of the diagram that holds the step: alt, opt, par or loop, with its label.",
        "who_atlas": "Actor that acts, as named in the atlas.",
        "who_node": "Box of that actor.",
        "who_role": "Role of that actor.",
        "to_atlas": "Actor that receives, as named in the atlas.",
        "to_node": "Box of that actor.",
        "to_role": "Role of that actor.",
        "own_action": "yes when the actor acts alone (a note or a message to itself).",
        "reply": "yes when the diagram draws the message as a reply.",
        "text": "Text of the step.",
        "flows": "Flows of flows.csv that the step shows, when one matches.",
        "basis": "Source codes as given in the step.",
    }),
    "actor_map": ("How each actor name of the sequence diagrams maps to a box and a role.", {
        "atlas_actor": "Actor name as written in the atlas.",
        "node_id": "Box.",
        "role_id": "Role.",
        "note": "Why the mapping was chosen, when it is not obvious.",
    }),
    "roles": ("Roles that act in the steps and the nets: a person, a body, a committee or a party outside government.", {
        "role_id": "Identifier.",
        "name": "Name of the role.",
        "node_id": "Box the role belongs to.",
        "kind": "person, body, committee or external.",
        "description": "What the role does.",
        "basis": "Source codes.",
    }),
    "chains": ("The curated process chains that are modelled as Petri nets.", {
        "chain_id": "Identifier.",
        "name": "Name of the chain.",
        "question": "Question the net answers.",
        "atlas_ref": "Diagrams and chapters of the atlas it is built from.",
    }),
    "places": ("Places of the Petri nets: states of a case, balances, records on their way between bodies (channel places, each named after its flow; a flow that carries two kinds of record has two), and moments of the calendar.", {
        "place_id": "Identifier. S- for a state, a balance or a moment of the calendar; C- and the flow number for a record on its way (C-F032, or C-F008-NCA when a flow has two channel places).",
        "kind": "state, balance, channel or clock.",
        "name": "What a token in the place means.",
        "line": "One of the four lines of the atlas: authority, claim, cash or records.",
        "records": "Records that a token stands for.",
        "flow_id": "For a channel, the flow it carries.",
        "initial": "Number of tokens at the start, when the place is marked.",
        "cohorts": "Cohorts in which the place exists.",
        "basis": "Source codes.",
    }),
    "place_holders": ("For each place and cohort, the box that holds the record: the system of record.", {
        "place_id": "Place.",
        "cohort": "Cohort, or all.",
        "held_in": "Box that holds the record in that cohort.",
        "basis": "Source codes.",
        "note": "Anything a reader should know.",
    }),
    "transitions": ("Transitions of the Petri nets: acts of a role in a body or system.", {
        "transition_id": "Identifier. The letters say the chain (SP spending, RL release, PR procurement, CO collections, TX taxes, DB borrowing, RP reporting, PL planning).",
        "chain_id": "Chain.",
        "name": "The act, as a verb.",
        "role_id": "Role that acts.",
        "node_id": "Box where the act happens.",
        "steps": "Steps of the atlas that show the act.",
        "rules": "Rules that the act must respect.",
        "cohorts": "Cohorts in which the act exists.",
        "basis": "Source codes.",
        "note": "Anything a reader should know.",
    }),
    "arcs": ("Arcs of the Petri nets, between a place and a transition.", {
        "transition_id": "Transition.",
        "place_id": "Place.",
        "direction": "in (the transition takes a token), out (it puts a token), read (it needs a token and leaves it).",
        "cohorts": "Cohorts in which the arc exists; all means every cohort of the transition.",
        "weight": "1, or amount when the arc moves an amount of money from a balance.",
    }),
    "bindings": ("For each transition and cohort, the ICONIX objects of the act: the boundary object (what the actor touches) and the control object (the check of the step).", {
        "transition_id": "Transition.",
        "cohort": "Cohort, or all.",
        "boundary": "Boundary object: the form, screen, portal or file.",
        "boundary_node": "Box of the boundary object, when it is a system.",
        "controller": "Control object: who or what checks the step.",
        "controller_kind": "person, software, bank or not_stated.",
        "writes_in": "Boxes in which the act writes its records.",
        "basis": "Source codes.",
        "note": "Anything a reader should know.",
    }),
    "rules": ("Rules that the nets respect: guards, invariants, deadlines and obligations.", {
        "rule_id": "Identifier.",
        "statement": "The rule, in one sentence.",
        "kind": "guard, invariant, deadline or obligation.",
        "transitions": "Transitions where the rule is checked.",
        "places": "For an invariant, the places that it relates.",
        "enforced_in_P": "Who or what enforces the rule in cohort P.",
        "enforced_in_E": "Who or what enforces the rule in cohort E.",
        "enforced_in_B": "Who or what enforces the rule in cohort B.",
        "basis": "Source codes.",
    }),
    "use_cases": ("ICONIX use cases of the curated chains. Each one is a group of transitions with one goal.", {
        "use_case_id": "Identifier.",
        "name": "Name of the use case.",
        "chain_id": "Chain.",
        "transitions": "Transitions of the basic course, in order.",
        "primary_role": "Primary actor.",
        "goal": "What is true when the use case ends well.",
        "alternate_courses": "Alternate courses, separated by a vertical bar, each with its sources.",
    }),
    "cohorts": ("Cohorts of agencies: the same act happens in different systems in different agencies.", {
        "cohort_id": "P, E or B.",
        "name": "Name.",
        "description": "Who is in the cohort and which systems they use.",
        "basis": "Source codes.",
        "note": "What is not known about the cohort.",
    }),
    "gaps": ("Open questions: what the sources do not say, or where they differ.", {
        "gap_id": "Identifier.",
        "status": "open, partly_settled or sources_differ.",
        "question": "The question.",
        "why_it_matters": "What depends on the answer.",
        "related": "Boxes, flows and records that the question touches.",
        "who_could_settle": "Who could answer it.",
        "what_would_settle": "What document or fact would answer it.",
        "atlas_ref": "Where the atlas raises it, if it does.",
        "basis": "Source codes.",
    }),
    "sources": ("The sources. Every basis column names codes of this table.", {
        "code": "Code used in the basis columns.",
        "type": "Kind of source, used to find the strongest source of a row.",
        "title": "Title.",
        "url": "Address, when the source is on the web.",
        "how_read": "How the source was read: in full, in part, a summary, or only its title.",
        "used_for": "What it was used for.",
        "origin": "Where the code comes from: the atlas (its Reference F), or new in this repository.",
    }),
    "vocab": ("Allowed values of the coded columns, with their meaning. The checks refuse any other value.", {
        "table": "Register.",
        "column": "Column.",
        "value": "Allowed value.",
        "meaning": "What the value means.",
    }),
}


def data_model_md(m):
    lines = ["# Data model", "",
             "This file is written by tools/build.py from tools/pfmmap/schema.py and model/vocab.csv. Do not edit it by hand.", "",
             "The registers are CSV files in model/, in UTF-8, with a header row. A list inside one cell is separated by semicolons. Every row with a basis column names at least one code of sources.csv. The program tools/check.py checks the identifiers, the allowed values and the sources, and the build stops when a check fails.", "",
             "| Register | Rows | What it holds |", "|---|---|---|"]
    for t in ORDER:
        lines.append(f"| [{t}.csv](#{t}) | {len(m.t[t])} | {TABLES[t][0]} |")
    lines.append("")
    vocab = {}
    for v in m.t["vocab"]:
        vocab.setdefault((v["table"], v["column"]), []).append((v["value"], v["meaning"]))
    for t in ORDER:
        purpose, cols = TABLES[t]
        lines += [f"## {t}", "", purpose, "", "| Column | Meaning |", "|---|---|"]
        for c in (list(m.t[t][0].keys()) if m.t[t] else list(cols)):
            text = cols.get(c, "(not described)")
            if (t, c) in vocab:
                text += " Values: " + "; ".join(f"`{v}` {mean[0].lower() + mean[1:] if mean else ''}".strip() for v, mean in vocab[(t, c)]) + "."
            lines.append(f"| {c} | {text} |")
        lines.append("")
    return "\n".join(lines)


def undocumented(m):
    out = []
    for t in m.t:
        if t not in TABLES:
            out.append(f"register {t} is not described in schema.py")
            continue
        if m.t[t]:
            for c in m.t[t][0].keys():
                if c not in TABLES[t][1]:
                    out.append(f"column {t}.{c} is not described in schema.py")
    return out
