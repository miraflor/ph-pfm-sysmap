# Data model

This file is written by tools/build.py from tools/pfmmap/schema.py and model/vocab.csv. Do not edit it by hand.

The registers are CSV files in model/, in UTF-8, with a header row. A list inside one cell is separated by semicolons. Every row with a basis column names at least one code of sources.csv. The program tools/check.py checks the identifiers, the allowed values and the sources, and the build stops when a check fails.

| Register | Rows | What it holds |
|---|---|---|
| [nodes.csv](#nodes) | 167 | The boxes of the map: institutions and parties (level 0), systems, accounts, networks, standards, websites and units (level 1), and modules (level 2). Every box has one parent, except the boxes of level 0. |
| [flows.csv](#flows) | 99 | What passes from one box to another: data, a document, an authority or money. The 69 rows of the register of interfaces of the atlas (its Reference B) are all here; a few are split in two or three, and new rows have no atlas row. |
| [records.csv](#records) | 155 | The documents, reports, registers, authorities, data and money that the flows carry and the nets hold. |
| [fields.csv](#fields) | 112 | Fields of the records, from diagram 17c of the atlas (its entity diagram). |
| [record_links.csv](#record_links) | 20 | Links between records, from diagram 17c of the atlas. |
| [steps.csv](#steps) | 336 | Every message and own action of the twenty sequence diagrams of the atlas, one row each, in the order of the diagram. |
| [actor_map.csv](#actor_map) | 115 | How each actor name of the sequence diagrams maps to a box and a role. |
| [roles.csv](#roles) | 66 | Roles that act in the steps and the nets: a person, a body, a committee or a party outside government. |
| [chains.csv](#chains) | 8 | The curated process chains that are modelled as Petri nets. |
| [places.csv](#places) | 123 | Places of the Petri nets: states of a case, balances, records on their way between bodies (channel places, each named after its flow; a flow that carries two kinds of record has two), and moments of the calendar. |
| [place_holders.csv](#place_holders) | 65 | For each place and cohort, the box that holds the record: the system of record. |
| [transitions.csv](#transitions) | 86 | Transitions of the Petri nets: acts of a role in a body or system. |
| [arcs.csv](#arcs) | 240 | Arcs of the Petri nets, between a place and a transition. |
| [bindings.csv](#bindings) | 102 | For each transition and cohort, the ICONIX objects of the act: the boundary object (what the actor touches) and the control object (the check of the step). |
| [rules.csv](#rules) | 19 | Rules that the nets respect: guards, invariants, deadlines and obligations. |
| [use_cases.csv](#use_cases) | 14 | ICONIX use cases of the curated chains. Each one is a group of transitions with one goal. |
| [cohorts.csv](#cohorts) | 3 | Cohorts of agencies: the same act happens in different systems in different agencies. |
| [gaps.csv](#gaps) | 26 | Open questions: what the sources do not say, or where they differ. |
| [sources.csv](#sources) | 133 | The sources. Every basis column names codes of this table. |
| [vocab.csv](#vocab) | 107 | Allowed values of the coded columns, with their meaning. The checks refuse any other value. |

## nodes

The boxes of the map: institutions and parties (level 0), systems, accounts, networks, standards, websites and units (level 1), and modules (level 2). Every box has one parent, except the boxes of level 0.

| Column | Meaning |
|---|---|
| node_id | Identifier. INST- for an institution, EXT- for a party outside government, SYS- for a system or a website, MOD- for a module, ACC- for an account, NET- for a network, STD- for a standard, UNIT- for a unit. |
| level | 0, 1 or 2. Values: `0` an institution or an outside party. The coarsest level of the map; `1` a system, a unit of an institution, an account, a network or a standard, inside an institution; `2` a module of a system, inside the system. |
| type | Kind of box. Values: `institution` a public body or a group of bodies of the same kind; `external` a party outside government; `unit` a unit or office inside an institution; `system` an information system; `module` a module, function or facility of a system; `account` a bank account or a group of accounts; `network` a government network; `standard` a standard or framework that systems must follow; `website` a website that publishes documents. |
| parent_id | The box that contains this one. Empty at level 0. |
| name | Short name, as drawn in the map. |
| full_name | Full name. |
| group | Part of PFM, used for the colour of the box: budget, procurement, treasury, revenue, banking, spending, audit, local, planning, ict, political, oversight, governance, finance, external, other. |
| status | Stage of use of a system (empty for institutions and units). Values: `in_use` a source describes it as existing today; `in_use_part` it exists, but only some agencies, banks or local governments use it; `described_not_verified` a rule or the owner describes it; no source confirms present use; `planned` a plan names it; it is not in production; `retiring` it is being closed according to a decision of its owner; `required_by_law` a law requires it; its present state is not verified; `not_stated` the sources read do not name or describe it; it exists by general knowledge. |
| scope | core for public financial management; adjacent for a system next to it (shown only when you ask for it). Values: `core` part of the public financial management of the national government; `adjacent` linked to PFM, but its flows with PFM systems are not described; hidden by default in the map. |
| owner | Body that owns or runs the system. |
| users | Who enters the data. |
| recipients | Who reads the data. |
| description | What it is and does, in a few sentences. Source codes in square brackets. |
| basis | Source codes for the row (see sources.csv). |
| atlas_ref | Where the atlas describes it. |
| since | Year or month from which it is in use, when a source states it. |
| note | Anything a reader should know before using the row. |

## flows

What passes from one box to another: data, a document, an authority or money. The 69 rows of the register of interfaces of the atlas (its Reference B) are all here; a few are split in two or three, and new rows have no atlas row.

| Column | Meaning |
|---|---|
| flow_id | Identifier. F and the number of the atlas row (F032); a letter is added when a row is split (F021A); numbers above 100 are new. |
| atlas_row | Number of the row in the register of the atlas. Empty for a new row. |
| side | Side of the atlas register: spending, revenue and treasury, inside one agency, or new. |
| domain | Part of PFM, used by the filters. Values: `planning_budget` investment program and budget preparation; `release` release of allotments and cash authority; `procurement` procurement; `execution` obligation, payment and their records; `reporting` reports to DBM, COA, BTr and the public; `assets` assets; `revenue` taxes, customs and agency collections; `treasury_debt` cash management, securities and debt; `local` local governments; `inside_agency` between units of one agency; `integration` planned connections of the IFMIS core. |
| from_id | Box that sends. |
| via_id | Box the flow passes through, when the source names one (for example the servicing bank between BTMS and the clearing house). |
| to_id | Box that receives. |
| what_passes | What passes, in words. |
| payload | Records that pass (see records.csv), separated by semicolons. |
| kind | data, document, authority or money. Values: `data` figures or records; `document` a signed paper, or a copy or file of it; `authority` a document that gives a right or sets a limit, for example an allotment or an NCA; `money` money moves between two accounts or persons. |
| agent | Who moves the content. The atlas has one word, the carrier; here it is split into two questions, agent and medium. Values: `program` one program sends to another, and no person copies the content; `sender_person` a person of the sending body enters or uploads the content in a system of the receiver or delivers signed copies; `receiver_person` a person of the receiving body takes the content from a system of the sender; `own_person` staff enter the content in a record or system of their own body; `not_stated` the sources do not say who moves the content; `not_applicable` money, or a publication that any person reads. |
| medium | How the content passes. Values: `paper` signed paper copies; `data_entry` a person types or uploads the content into a program (a portal or installed software); `download` a person of the receiving body downloads the content from a program of the sender (a file, or a page to print); `own_register` a person writes the content in a register of the own body: on paper or in a spreadsheet; `electronic_unspecified` a source describes an electronic channel, not its kind; `api` a program-to-program interface; for planned flows the plan names APIs; `payment_network` messages through a payment or settlement network between banks; `bank_transfer` money moves between bank accounts; `cash_or_check` cash or check handed over; `public_website` published on a website for any person; `not_stated` the sources do not say how the content passes. |
| atlas_carrier | The carrier of the atlas, as written there. |
| stage | Stage of use. Values: `in_use` a source describes the flow as existing today; `in_use_part` the flow exists for some agencies or banks only; `described_not_verified` a rule or the owner describes or requires it; no source confirms use; `planned` a plan names it; `not_stated` the sources do not say whether it is in use. |
| cohorts | Cohorts in which the flow exists (P, E, B, or all). |
| timing | When or how often it passes, when a source states it. |
| standard | Message standard, when a source states it. |
| check | How the two sides check each other, as in the atlas. |
| basis | Source codes for the row. |
| gaps | Open questions about the row (see gaps.csv). |
| note | Anything a reader should know before using the row. |
| atlas_from | The sender as written in the atlas. |
| atlas_to | The receiver as written in the atlas. |

## records

The documents, reports, registers, authorities, data and money that the flows carry and the nets hold.

| Column | Meaning |
|---|---|
| record_id | Identifier, R- and a short name (R-LDDAP). |
| name | Name of the record, with its form number when it has one. |
| kind | Kind of record. Values: `authority` a document that gives a right or sets a limit; `document` a form or paper of the process; `data` data held in a system, without a form of its own; `report` a periodic report or statement; `register` a registry or ledger that is kept over time; `money` a movement of money; `message` a message between programs. |
| issuer | Who issues or signs it. |
| issuer_node | Box of the issuer. |
| purpose | What it is for. |
| identified_by | How one record is told apart from another (its number). |
| form_ref | Appendix of the Government Accounting Manual or other form number. |
| basis | Source codes for the row. |
| atlas_ref | Where the atlas describes it. |
| note | Anything a reader should know. |

## fields

Fields of the records, from diagram 17c of the atlas (its entity diagram).

| Column | Meaning |
|---|---|
| record_id | Record that has the field. |
| order | Order of the field in the record. |
| field | Name of the field. |
| type | string, code, money, text or date. |
| key | PK for the field that identifies the record, FK for a field that points to another record, empty otherwise. |
| references | For an FK, the record it points to. |
| note | Note of the atlas on the field. |
| basis | Source codes; GK when the atlas marks it as general knowledge. |
| atlas_ref | Where the atlas has it. |

## record_links

Links between records, from diagram 17c of the atlas.

| Column | Meaning |
|---|---|
| link_id | Identifier. |
| from_record | Record on the side of one. |
| to_record | Record on the side of many. |
| relation | Verb of the link, as in the atlas. |
| key | Field that carries the link. Empty when the source does not state it. |
| cardinality | Cardinality in the notation of Mermaid entity diagrams (||--o{ is one to zero or more). |
| basis | Diagram 17c, or GK when the atlas marks the link as general knowledge. |
| atlas_ref | Where the atlas has it. |

## steps

Every message and own action of the twenty sequence diagrams of the atlas, one row each, in the order of the diagram.

| Column | Meaning |
|---|---|
| step_id | Diagram and number of the step (07a-05). |
| diagram_id | Diagram of the atlas. |
| step | Number of the step in the diagram. |
| section | Note of the diagram that comes before the step, when there is one. |
| block | Block of the diagram that holds the step: alt, opt, par or loop, with its label. |
| who_atlas | Actor that acts, as named in the atlas. |
| who_node | Box of that actor. |
| who_role | Role of that actor. |
| to_atlas | Actor that receives, as named in the atlas. |
| to_node | Box of that actor. |
| to_role | Role of that actor. |
| own_action | yes when the actor acts alone (a note or a message to itself). |
| reply | yes when the diagram draws the message as a reply. |
| text | Text of the step. |
| flows | Flows of flows.csv that the step shows, when one matches. |
| basis | Source codes as given in the step. |

## actor_map

How each actor name of the sequence diagrams maps to a box and a role.

| Column | Meaning |
|---|---|
| atlas_actor | Actor name as written in the atlas. |
| node_id | Box. |
| role_id | Role. |
| note | Why the mapping was chosen, when it is not obvious. |

## roles

Roles that act in the steps and the nets: a person, a body, a committee or a party outside government.

| Column | Meaning |
|---|---|
| role_id | Identifier. |
| name | Name of the role. |
| node_id | Box the role belongs to. |
| kind | person, body, committee or external. Values: `person` a person in a position; `body` a body or an office; `committee` a committee; `external` a party outside government. |
| description | What the role does. |
| basis | Source codes. |

## chains

The curated process chains that are modelled as Petri nets.

| Column | Meaning |
|---|---|
| chain_id | Identifier. |
| name | Name of the chain. |
| question | Question the net answers. |
| atlas_ref | Diagrams and chapters of the atlas it is built from. |

## places

Places of the Petri nets: states of a case, balances, records on their way between bodies (channel places, each named after its flow; a flow that carries two kinds of record has two), and moments of the calendar.

| Column | Meaning |
|---|---|
| place_id | Identifier. S- for a state, a balance or a moment of the calendar; C- and the flow number for a record on its way (C-F032, or C-F008-NCA when a flow has two channel places). |
| kind | state, balance, channel or clock. Values: `state` a condition that is true or not yet true for one case; `balance` an amount that many cases share (allotment, NCA, cash); `channel` a record on its way from one body to another: the place of one flow; `clock` a moment of the calendar. |
| name | What a token in the place means. |
| line | One of the four lines of the atlas: authority, claim, cash or records. Values: `authority` the line of legal authority (blue in the atlas); `claim` the line of the claim: contract, work, acceptance (green); `cash` the line of cash (orange); `records` the line of records, reports and audit (grey). |
| records | Records that a token stands for. |
| flow_id | For a channel, the flow it carries. |
| initial | Number of tokens at the start, when the place is marked. |
| cohorts | Cohorts in which the place exists. |
| basis | Source codes. |

## place_holders

For each place and cohort, the box that holds the record: the system of record.

| Column | Meaning |
|---|---|
| place_id | Place. |
| cohort | Cohort, or all. |
| held_in | Box that holds the record in that cohort. |
| basis | Source codes. |
| note | Anything a reader should know. |

## transitions

Transitions of the Petri nets: acts of a role in a body or system.

| Column | Meaning |
|---|---|
| transition_id | Identifier. The letters say the chain (SP spending, RL release, PR procurement, CO collections, TX taxes, DB borrowing, RP reporting, PL planning). |
| chain_id | Chain. |
| name | The act, as a verb. |
| role_id | Role that acts. |
| node_id | Box where the act happens. |
| steps | Steps of the atlas that show the act. |
| rules | Rules that the act must respect. |
| cohorts | Cohorts in which the act exists. |
| basis | Source codes. |
| note | Anything a reader should know. |

## arcs

Arcs of the Petri nets, between a place and a transition.

| Column | Meaning |
|---|---|
| transition_id | Transition. |
| place_id | Place. |
| direction | in (the transition takes a token), out (it puts a token), read (it needs a token and leaves it). Values: `in` the transition consumes a token of the place; `out` the transition produces a token in the place; `read` the transition needs a token of the place, and leaves it. |
| cohorts | Cohorts in which the arc exists; all means every cohort of the transition. |
| weight | 1, or amount when the arc moves an amount of money from a balance. |

## bindings

For each transition and cohort, the ICONIX objects of the act: the boundary object (what the actor touches) and the control object (the check of the step).

| Column | Meaning |
|---|---|
| transition_id | Transition. |
| cohort | Cohort, or all. |
| boundary | Boundary object: the form, screen, portal or file. |
| boundary_node | Box of the boundary object, when it is a system. |
| controller | Control object: who or what checks the step. |
| controller_kind | person, software, bank or not_stated. Values: `person` a person makes the check and signs; `software` a program makes the check; `bank` the bank makes the check; `not_stated` the sources do not describe who checks. |
| writes_in | Boxes in which the act writes its records. |
| basis | Source codes. |
| note | Anything a reader should know. |

## rules

Rules that the nets respect: guards, invariants, deadlines and obligations.

| Column | Meaning |
|---|---|
| rule_id | Identifier. |
| statement | The rule, in one sentence. |
| kind | guard, invariant, deadline or obligation. Values: `guard` a condition that must hold before a transition fires; `invariant` a condition that must hold between places at the end of a period; `deadline` a time limit; `obligation` an act that must follow another act. |
| transitions | Transitions where the rule is checked. |
| places | For an invariant, the places that it relates. |
| enforced_in_P | Who or what enforces the rule in cohort P. |
| enforced_in_E | Who or what enforces the rule in cohort E. |
| enforced_in_B | Who or what enforces the rule in cohort B. |
| basis | Source codes. |

## use_cases

ICONIX use cases of the curated chains. Each one is a group of transitions with one goal.

| Column | Meaning |
|---|---|
| use_case_id | Identifier. |
| name | Name of the use case. |
| chain_id | Chain. |
| transitions | Transitions of the basic course, in order. |
| primary_role | Primary actor. |
| goal | What is true when the use case ends well. |
| alternate_courses | Alternate courses, separated by a vertical bar, each with its sources. |

## cohorts

Cohorts of agencies: the same act happens in different systems in different agencies.

| Column | Meaning |
|---|---|
| cohort_id | P, E or B. Values: `P` paper and own registers; `E` cOA eBudget and eNGAS; `B` bTMS; `all` all cohorts. |
| name | Name. |
| description | Who is in the cohort and which systems they use. |
| basis | Source codes. |
| note | What is not known about the cohort. |

## gaps

Open questions: what the sources do not say, or where they differ.

| Column | Meaning |
|---|---|
| gap_id | Identifier. |
| status | open, partly_settled or sources_differ. Values: `open` no source read settles it; `partly_settled` some part is settled by a source; `sources_differ` sources read disagree. |
| question | The question. |
| why_it_matters | What depends on the answer. |
| related | Boxes, flows and records that the question touches. |
| who_could_settle | Who could answer it. |
| what_would_settle | What document or fact would answer it. |
| atlas_ref | Where the atlas raises it, if it does. |
| basis | Source codes. |

## sources

The sources. Every basis column names codes of this table.

| Column | Meaning |
|---|---|
| code | Code used in the basis columns. |
| type | Kind of source, used to find the strongest source of a row. Values: `law` a law or the Constitution; `executive_issuance` an order or circular of the President; `budget_law` a part of a General Appropriations Act; `rule` a circular, manual, implementing rule or form: it says what must happen; `owner_statement` a page, release or publication of the body that owns the subject: it says what exists or is planned; `plan` a reform plan or action plan; `assessment` an independent assessment; `press` a press report or another secondary source; `vendor` a statement of a vendor about its own product or client; `record_instance` real documents that agencies filled and published; `general_knowledge` not read in a source; `inference` a reading of this repository; not stated in a source. |
| title | Title. |
| url | Address, when the source is on the web. |
| how_read | How the source was read: in full, in part, a summary, or only its title. |
| used_for | What it was used for. |
| origin | Where the code comes from: the atlas (its Reference F), or new in this repository. |

## vocab

Allowed values of the coded columns, with their meaning. The checks refuse any other value.

| Column | Meaning |
|---|---|
| table | Register. |
| column | Column. |
| value | Allowed value. |
| meaning | What the value means. |
