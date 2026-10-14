# Philippine PFM Systems Map

A map of the information systems of Philippine public financial management (PFM), seen from information technology: which systems exist, who owns them, who enters and reads their data, and what passes between them. What passes can be data, a document, an authority (such as an allotment or a cash authority) or money.

One set of registers feeds everything in this repository: an interactive map with three levels of detail, static maps, Petri nets of the main processes, and ICONIX models (a domain model, use cases, robustness diagrams and sequence diagrams).

Source register and targeted review current to 13 October 2026. Deployment and interface claims are not certified: see [EVIDENCE_REVIEW.md](EVIDENCE_REVIEW.md). This is an independent reference. It is not an official publication of the Philippine government, and it is not part of any other project.

**Theme:** light mode is the default even on computers using dark mode. Dark mode is available via a clearly labelled toggle in the header; the explicit preference is remembered in the browser.

## Open the map

Open `docs/index.html` in a web browser. The page works without a network connection, because the drawing library (Cytoscape.js) is in `docs/vendor/`. The fonts come from Google Fonts when a connection exists; without one, the page uses the fonts of the computer.

If GitHub Pages is turned on for the folder `docs/` of this repository, the same page is the web site of the repository.

The page has four tabs:

| Tab | What it shows |
|---|---|
| Map | All institutions, systems, units and modules in one map, with every flow between them. Choose level 0, 1 or 2, or open and close one box at a time with a double-click. Click a box or a line to read about it. Filters, a cohort selector and a search box are at the top. |
| Process nets | The Petri nets: eight curated chains, each for cohort P, E or B, and twenty workflow nets made from the sequence diagrams of the atlas. Click a place or a transition to read about it. |
| Lists | Every flow, every system, every open question and every source, as tables. |
| How to read | The legend, the cohorts and the rules of evidence. |

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for build commands, semantic limits and automated checks.

## What is in the repository

| Folder or file | What it holds |
|---|---|
| `model/` | The registers, as CSV files. They are the source of truth: everything else is made from them. `docs/DATA_MODEL.md` describes every column. |
| `atlas_extract/` | What `tools/import_atlas.py` read from the atlas: its tables, its twenty sequence diagrams and its entity diagram. Do not edit these files. |
| `maps/` | Static maps made with Graphviz, as SVG (to look at) and DOT (to change). |
| `petri/` | The Petri nets as PNML (to open in Petri net tools), DOT and SVG, and `petri/ANALYSIS.md`. |
| `iconix/` | The ICONIX models as PlantUML files with SVG drawings, and `iconix/USE_CASES.md`. |
| `docs/` | The interactive page, evidence review and description of the data model. |
| `audit/` | Targeted public-source claim reviews, with dates and links. |
| `exports/` | Reproducible GraphML network for graph analysis. |
| `tools/` | The programs that check the registers and build everything. |
| `REPORT.md` | Counts and results of the last build. |

## The map in three levels

Level 0 has 30 institutions and 7 parties outside government (suppliers and payees, employees, beneficiaries, dealers and lenders, taxpayers and importers, payers of fees, and the public). Level 1 has what is inside each institution: 55 systems, 41 units, 2 accounts (the Treasury Single Account and the MDS sub-accounts), 1 network, 1 standard and 1 website. Level 2 has 29 modules of the systems that have them, for example the 9 modules of BTMS and the 11 modules of the modernized PhilGEPS.

Level 0 alone is drawn in a small layout, so that all of it can be read on one screen. From level 1 on, every box keeps its place: a closed box takes the space that its contents take when it is open, so opening or closing a box does not move the other boxes. In both layouts the institutions stand in the same zones: authority and budget on the left, the spending agency in the middle, banks, the Treasury and revenue on the right, parties outside government at the far right, and oversight and the public on top.

When two closed boxes have several flows between their contents, one line joins them, and its number is the count of flows. Open a box to see each flow as its own line.

A line is drawn this way:

| Feature of the line | Meaning |
|---|---|
| Colour | What passes: blue for an authority, green for a document, grey for data, orange for money. |
| Pattern | How it passes: dotted for paper; dashed when a person enters, uploads or downloads it; thick for a program-to-program interface or a payment network; thin when the channel is electronic but its kind is not stated, or when the sources do not say. |
| Hollow arrow | A planned flow. |
| Faint line | Described by a rule or by the owner, but its use is not verified. |

## How a flow is described

Each flow has a sender, a receiver, and sometimes a body it passes through (for example the servicing bank, between BTMS and the clearing house). It also has what passes, the records it carries, its kind, its stage of use, the cohorts in which it exists, the check that the two sides make, its sources, and the open questions about it.

The atlas describes how a flow passes with one word, the carrier. Here the carrier is split into two questions, and the carrier of the atlas is kept beside the answers. The first question is who moves the content: a program, a person of the sender, a person of the receiver, or a person of the own body. The second question is the medium: paper, data entry, a download, an own register, an electronic channel of unstated kind, a program interface (API), a payment network, a bank transfer, cash or check, or a public website.

All 69 rows of the register of interfaces of the atlas are here, as 75 flows (some rows are split in two or three, because they join two different flows). 24 flows are new in this repository. Twelve of them are planned: nine connections that the IFMIS plan describes between BTMS and other systems, two inputs to the cash flow forecasting module of BTMS, and documents from a planned document management system. Three are described in the order on the COMPASS portal. The others come from the BTMS circular (reports made from BTMS, payment by electronic transfer), from statements of DBM, DILG and the Land Bank, and from the circular on the release of funds for 2026.

## Cohorts

The same act happens in different systems in different agencies. For example, an agency may keep its registry of obligations on paper, in the eBudget system of COA, or in BTMS. The registers therefore use three cohorts:

| Cohort | Agencies |
|---|---|
| P | Agencies that keep their registries and books on paper, in spreadsheets or in their own software. |
| E | Agencies that keep their registries in the eBudget system of COA and their books in eNGAS. |
| B | Agencies in the rollout of BTMS. |

A flow, a place, a transition or an arc can exist in some cohorts only. How many agencies are in each cohort is not stated in the sources (see the open question GAP-BTMS-SCALE).

## Process nets

A Petri net is a model of a process with places (circles: states, balances, records), transitions (boxes: acts) and tokens (marks in the places). A transition can fire when its input places hold tokens; it takes them and puts tokens in its output places.

The curated chains are spending, release of allotments, procurement up to the award, collections of an agency, tax and customs collections, borrowing, reporting, and planning up to the enacted budget. Each chain has one net for each cohort, and one more net joins all the chains. Their places are of four kinds: states of a case, balances (an amount that many cases share, such as the NCA balance), records on their way between two bodies (channel places, each named after its flow in the map), and moments of the calendar. A read arc means that a transition needs a token and leaves it, for example a check against a balance that does not change it.

For each place and cohort, `model/place_holders.csv` names the system or body that holds the record: the system of record. For each transition and cohort, `model/bindings.csv` names what the actor touches and who or what checks the step.

The workflow nets are made from the twenty sequence diagrams of the atlas: one start place, one end place, one transition for each message or own action, and silent transitions for the blocks of the diagram. The build checks each of them by searching all the markings it can reach. The twenty **generated block-structured workflow nets** pass the finite-state reachability/soundness check on the models as constructed: from each reachable marking an end state is reachable, completion leaves no other token, and all model transitions are reachable. This result does **not** validate the source processes, legal compliance or monetary balances.

The nets are written in PNML, the standard exchange format for Petri nets (ISO/IEC 15909-2), as place/transition nets. A read arc is written there as two arcs, one in each direction. `petri/ANALYSIS.md` lists, for each net, its size, where it starts and where it ends. It also shows the acts that change one record of the NCA balance and not the others: these acts open a window in which the records of the accounting unit, the cash unit and the bank differ, and the monthly reconciliation is where the difference is found.

## ICONIX models

ICONIX is a method of modelling that goes from a domain model and use cases to robustness diagrams and then to sequence diagrams. A robustness diagram has four kinds of object: the actor (a person or body), the boundary object (what the actor touches: a form, a screen, a portal), the control object (the check or the logic of one step) and the entity object (a stored record).

The folder `iconix/` has:

| File | What it holds |
|---|---|
| `domain_model.puml` | The records of diagram 17c of the atlas, with their fields and links. |
| `use_case_diagram.puml` | The 14 system use cases of the curated chains, with their actors. |
| `robustness/` | One robustness diagram for each use case and each group of cohorts in which the use case differs: 30 diagrams. |
| `sequence/` | One sequence diagram for each of the same 30 variants. |
| `USE_CASES.md` | The text of every system use case (basic course and alternate courses, by cohort), and 20 business use cases made from the sequence diagrams of the atlas. |

The build checks the four *syntactic linking rules* of the robustness diagram (an actor touches only boundary objects; an entity object connects only to control objects; and so on). The last build found no link that breaks them.

## Rules of evidence

Every box, flow, record, place, transition and rule names its sources, by codes of `model/sources.csv`. The page shows the strongest kind of source of each row (law, circular or manual, statement of the owner, plan, press report, and so on).

"Not stated" never means "absent". It means that the sources read do not say.

"GK" marks general knowledge that was not read in a source. "INFERENCE" marks a reading of this repository that joins facts of the sources but is not stated in any of them. Both are shown wherever they are used.

A planned system or flow is never shown as in use. Two systems drawn near each other are not taken as connected: only a flow connects them.

Where the sources disagree, or do not say something that matters, the question is in `model/gaps.csv`, with who could answer it and what document would answer it. There are 26 such questions.

## What this map cannot tell

The physical layer is mostly not public: servers, hosting, networks between agencies, and the formats of the messages between systems. The sources state some of it: the payment networks (PhilPaSSplus, PESONet, InstaPay), the use of ISO 20022 between banks, and a statement of the vendor that BTMS runs in a cloud deployment. The rest is marked as not stated.

The registers describe the national government in more detail than local governments and government corporations.

## Build it yourself

You need Python 3.9 or later (the programs use the standard library only) and Graphviz (the program `dot`). To draw the ICONIX diagrams as SVG you also need Java and the file `plantuml.jar` of PlantUML; it is not in this repository because its licence differs. Point the environment variable `PLANTUML_JAR` to the file.

| Command | What it does |
|---|---|
| `python tools/check.py` | Checks the registers: identifiers, allowed values, cohorts, and sources. It prints every problem and ends with the number of problems. |
| `python tools/build.py` | Checks, then writes `maps/`, `petri/`, `iconix/`, `docs/index.html`, `docs/DATA_MODEL.md` and `REPORT.md`. It stops if the check finds a problem. |
| `python tools/build.py --page-only` | Checks, then writes the page only. |
| `python tools/import_atlas.py PATH` | Reads a copy of the atlas at PATH again and writes `atlas_extract/`. |

To change the map, change the CSV files of `model/` and build again. For example, a new system is one row of `nodes.csv` (with its parent, level, status and sources), and a new flow is one row of `flows.csv`. A new source is one row of `sources.csv`. The check says what is missing.

## Sources and credit

The main source is the Philippine PFM Atlas (https://github.com/miraflor/philippine-pfm-atlas): its register of interfaces, its inventory of systems, its sequence diagrams, its entity diagram of records and its list of sources. The codes of the sources of the atlas are kept as they are. Thirteen sources were added in this repository: statements of DBM, DILG and the Land Bank; statements of the vendors of BTMS and of PhilPaSSplus; four press reports; a summary of the E-Governance Act; and the action plan on cash management of the midterm update of the PFM reform roadmap. Two codes were added too: GK for general knowledge and INFERENCE for inferences. `model/sources.csv` says how each source was read. Some were read only as summaries, and the file says so.

The page uses Cytoscape.js 3.33.1, which has the MIT licence; its licence text is in `docs/vendor/`. No licence is granted for the rest of this repository.

## Words used here

| Word | Meaning |
|---|---|
| PFM | Public financial management: the budget, its release, spending, cash, revenue, debt, accounting, reporting and audit. |
| IFMIS | Integrated financial management information system: one system, or connected systems, for the whole of PFM. In the Philippines, BTMS is its core. |
| BTMS | Budget and Treasury Management System, of DBM and the Bureau of the Treasury (BTr). |
| GAA | General Appropriations Act: the budget law of a year. |
| SARO | Special Allotment Release Order: an authority to commit funds. |
| NCA | Notice of Cash Allocation: an authority to pay, up to a limit, from the MDS sub-account at the servicing bank. |
| MDS | Modified Disbursement System: payments of agencies through sub-accounts at servicing banks, which the Treasury then funds. |
| TSA | Treasury Single Account: the accounts of the Treasury at the BSP. |
| ORS, DV, JEV | Obligation Request and Status, Disbursement Voucher, Journal Entry Voucher: forms of the Government Accounting Manual. |
| LDDAP-ADA | List of Due and Demandable Accounts Payable with Advice to Debit Account: the payment order of an agency to its servicing bank. |
| Cohort | A group of agencies that do the same acts in the same systems (P, E or B here). |
| Channel place | A place of a Petri net that holds a record on its way between two bodies. It has the name of its flow in the map. |
| System of record | The system or body that holds the official copy of a record. |
| Read arc | An arc of a Petri net that needs a token and leaves it. |
| Workflow net | A Petri net with one start place and one end place. |
| Sound | Said of a workflow net that can always finish, finishes clean, and has no act that can never happen. |
| PNML | Petri Net Markup Language, the standard exchange format for Petri nets. |
| PlantUML | A text language for UML diagrams, used here for the ICONIX diagrams. |
