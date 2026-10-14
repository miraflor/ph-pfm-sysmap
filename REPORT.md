# Report of the build

Written by tools/build.py. Facts as of 2026-10-13.

## Registers

| Register | Rows |
|---|---|
| model/nodes.csv | 167 |
| model/flows.csv | 99 |
| model/records.csv | 155 |
| model/fields.csv | 112 |
| model/record_links.csv | 20 |
| model/steps.csv | 336 |
| model/actor_map.csv | 115 |
| model/roles.csv | 66 |
| model/chains.csv | 8 |
| model/places.csv | 123 |
| model/place_holders.csv | 65 |
| model/transitions.csv | 86 |
| model/arcs.csv | 240 |
| model/bindings.csv | 102 |
| model/rules.csv | 19 |
| model/cohorts.csv | 3 |
| model/gaps.csv | 26 |
| model/sources.csv | 133 |
| model/vocab.csv | 107 |
| model/use_cases.csv | 14 |

## Boxes of the map

| Level | Type | Count |
|---|---|---|
| 0 | external | 7 |
| 0 | institution | 30 |
| 1 | account | 2 |
| 1 | network | 1 |
| 1 | standard | 1 |
| 1 | system | 55 |
| 1 | unit | 41 |
| 1 | website | 1 |
| 2 | module | 29 |

Systems by status:

- in_use: 28
- planned: 12
- in_use_part: 7
- described_not_verified: 5
- not_stated: 2
- retiring: 1

## Flows

99 flows. 75 come from the 69 rows of the register of the atlas (some rows are split in two or three). 24 are new in this repository.

By kind: data 65, document 20, money 12, authority 2.

By stage: in_use 59, planned 13, not_stated 10, described_not_verified 9, in_use_part 8.

By agent: not_stated 32, sender_person 26, not_applicable 18, program 18, own_person 4, receiver_person 1.

By medium: not_stated 26, data_entry 18, api 13, bank_transfer 10, paper 10, electronic_unspecified 9, public_website 6, own_register 2, payment_network 2, cash_or_check 2, download 1.

By domain: execution 21, revenue 17, reporting 16, integration 9, planning_budget 7, procurement 7, treasury_debt 7, release 6, local 4, inside_agency 4, assets 1.

Strongest source of each flow: rule 47, owner_statement 17, plan 12, general_knowledge 8, press 8, law 5, assessment 1, budget_law 1. Flows whose basis includes general knowledge (GK): 11.

## Process steps

336 steps from 20 sequence diagrams of the atlas. 62 are own actions (a body acts alone). 66 are linked to a flow of the register. The other steps pass a document or a request that the register does not list as a flow between systems; the map shows them when you tick Process steps.

## Maps

| File | What it shows | Flows |
|---|---|---|
| maps/L0_institutions.svg | Level 0: institutions and parties; one line for each pair, with the number of flows | 96 |
| maps/L1_systems_now.svg | Level 1: systems and units, without the planned flows | 83 |
| maps/L1_systems_with_plans.svg | Level 1: systems and units, with the planned flows | 96 |
| maps/L2_modules.svg | Level 2: modules of BTMS, PhilGEPS and other systems | 96 |
| maps/by_domain/L1_assets.svg | Level 1, one part of PFM: Assets | 1 |
| maps/by_domain/L1_execution.svg | Level 1, one part of PFM: Obligation, payment and their records | 21 |
| maps/by_domain/L1_inside_agency.svg | Level 1, one part of PFM: Between units of one agency | 4 |
| maps/by_domain/L1_integration.svg | Level 1, one part of PFM: Planned connections of the IFMIS core | 9 |
| maps/by_domain/L1_local.svg | Level 1, one part of PFM: Local governments | 2 |
| maps/by_domain/L1_planning_budget.svg | Level 1, one part of PFM: Investment program and budget preparation | 7 |
| maps/by_domain/L1_procurement.svg | Level 1, one part of PFM: Procurement | 7 |
| maps/by_domain/L1_release.svg | Level 1, one part of PFM: Release of allotments and cash authority | 6 |
| maps/by_domain/L1_reporting.svg | Level 1, one part of PFM: Reports to DBM, COA, BTr and the public | 15 |
| maps/by_domain/L1_revenue.svg | Level 1, one part of PFM: Taxes, customs and agency collections | 17 |
| maps/by_domain/L1_treasury_debt.svg | Level 1, one part of PFM: Cash management, securities and debt | 7 |
| maps/L1_adjacent.svg | Level 1: flows that touch systems adjacent to PFM | 3 |

## Process nets

27 curated chain nets (chains by cohort, and all chains together by cohort) and 20 workflow nets of the sequence diagrams. Sound *generated block-structured workflow nets* under the finite-state model: 20 of 20; this does not prove the real government processes correct or their financial values consistent. Details in petri/ANALYSIS.md.

- R-NCA-EQUAL, cohort B: 4 transitions touch a subset of NCA-record places (potential reconciliation timing windows; amounts not simulated).
- R-NCA-EQUAL, cohort E: 6 transitions touch a subset of NCA-record places (potential reconciliation timing windows; amounts not simulated).
- R-NCA-EQUAL, cohort P: 6 transitions touch a subset of NCA-record places (potential reconciliation timing windows; amounts not simulated).

## ICONIX

14 system use cases, drawn in 30 cohort variants (robustness and sequence diagram for each), 20 business use cases, one domain model and one use case diagram: 62 PlantUML files. Links that break the four rules of robustness diagrams: 0. SVG drawings: not rerendered (PlantUML was not configured; existing SVGs may be stale).

## Open questions

| Status | Count |
|---|---|
| open | 22 |
| partly_settled | 3 |
| sources_differ | 1 |

## Page

- docs/index.html: 923 KB, with the data of all the registers inside
