# Evidence review · 13 October 2026

The full 266-row verification queue lives in `audit/verification_inventory.csv`; this is a targeted, independent review of important claims in this map. **It is not an audit of all source pages, systems, 99 flows, deployment counts, or transactions.** A cited law or circular supports a prescribed procedure; it is not evidence that every agency uses it. Each separately reviewed claim appears in `audit/claim_reviews.csv` and on the map's reading panel. Unreviewed claims are labelled accordingly.

## Findings and corrections

| Question | Finding | Consequence |
|---|---|---|
| Is the IFMIS fully operational nationwide? | No such conclusion is supported here. DBM speeches describe seven pilot agencies in 2025 and a 155-agency expansion **target** for 2026; DBM Circular Letter 2025-8 prescribes a phased rollout. Separately, the June 2026 SFA6 action plan gives a **baseline** of just two onboarded agencies and 0.00030% of pilot-agency budget executed through BTMS. The baseline, the piloting claims, and the target are not interchangeable operational counts. | BTMS stays `in_use_part`; the map's BTMS cohort is a modelling scenario, not a count of deployed agencies. |
| Is there currently no cross-system project identifier for PIPOL to OSBPS? | Older roadmap texts report an unresolved cross-system identifier and linkage gap. That does not by itself establish its persistence in October 2026. | The map now treats the gap as historical and keeps the live integration, crosswalk and matching method as open questions. |
| Are planned BTMS integrations live APIs? | Roadmap materials describe desired interfaces and integration pathways, not production traffic logs or published technical endpoint contracts. | Planned flows remain planned; interfaces with unspecified carriers remain unspecified. |
| Is the modernized PhilGEPS completely deployed? | RA 12009 and its IRR define system requirements, while GPPB Resolution 09-2025 describes pilot usage and an **indicative** retirement schedule for the legacy system. | Avoid treating statutory features or target dates as confirmed real-world functionality or completed decommissioning. |
| Which NGPA IRR is authoritative? | GPPB-TSO Public Advisory 09-2026 (31 July 2026) withdrew an unofficial March 2026 edition and directed users to the February 2025 GPPB-approved IRR. | Preserve the official 2025 IRR as the legal basis. Do not use the withdrawn version. |
| Are DBM eBudget and Project DIME operational? | DBM ICTSS helpdesk documented access to DBM eBudget in 2025; DBM reported the revived DIME and an October 2025 launch of its flood-control component. | Mark both as partially in use; do not equate access documentation or one launched component with nationwide completeness. |
| Is eNGAS/eBudget/AFRS documented by COA? | COA Government Accountancy Sector describes these systems and provides training/implementation resources. | Supports system existence and stated purpose, not agency-by-agency operational counts. |
| Are UACS and its cross-system classification mandatory? | DBM publishes Joint Circular 2013-1, subsequent amendments, and a description of UACS as a harmonized budget/treasury/accounting code structure. | Keep UACS as a coding standard, not as proof that all interfaces exchange identical records automatically. |
| Is the NCA equality rule literally always satisfied? | No. The three-record equality rule in the model is an analytical **reconciliation objective**. The graph's transitions do not carry numeric balances, timestamps, fund clusters or settlement data. | Reworded the rule and analysis to describe *possible timing windows*, not established numerical discrepancies or successful reconciliation. |
| Do the 20 sound workflow nets prove compliant government processes? | No. These are transformations of **the 20 source sequence diagrams** into block-structured workflow nets. Exhaustive reachability within each generated model checks its structure, not the real workflows. | Clarified the claim in site, README, Petri analysis and report; tests exercise actual generated PNML and soundness algorithms. |
| Do all 'in use' nodes have independently reviewed operational evidence? | No. One node (BPMS) remains `described_not_verified` after review. DBM primary sources provided additional evidence of partial use for DBM eBudget and Project DIME, so these two were restored to `in_use_part` with explicit scope limits. Other rows require individual review. | Avoid inferring operational deployment from a reform plan. |

## Public sources checked during this pass

- DBM, [Circular Letter 2025-8](https://www.dbm.gov.ph/index.php?catid=373&id=3566%3Acircular-letter-no-2025-8&view=article), phased BTMS adoption (28 August 2025).
- DBM, [2026 budget speech](https://www.dbm.gov.ph/index.php/the-secretary-2/speeches/3800-the-2026-people-s-budget-a-catalyst-for-a-future-ready-philippine-economy), seven initial pilot agencies and intended 155 agencies (22 January 2026).
- DBM, [Digital PFM (SFA6) reform action plan](https://www.dbm.gov.ph/wp-content/uploads/DBM%20Publications/PFM-Reforms/Midterm-Update/Action-Plans/SFA%206-%20Digital%20PFM-v3.pdf), baseline/target cells for BTMS pilot and rollout (2026 midterm update).
- DBM, [PFM Reforms Roadmap 2024–2028 Midterm Update](https://www.dbm.gov.ph/wp-content/uploads/DBM%20Publications/PFM-Reforms/Midterm-Update/PHIL%20PFM%20Roadmap%20Midterm%20Update%20v2.pdf), reform gaps and implementation agenda (June 2026).
- GPPB, [Resolution 09-2025](https://www.gppb.gov.ph/wp-content/uploads/2025/11/GPPB_Resolution_No._09-2025.pdf), PhilGEPS transition schedule (25 September 2025).
- GPPB-TSO, [Public Advisory 09-2026](https://www.gppb.gov.ph/public-advisory-no-09-2026/), warning that the unofficial IRR 1st Edition of March 2026 had been withdrawn (31 July 2026).
- [GPPB official IRR announcement](https://www.gppb.gov.ph/exciting-announcement-issuance-and-publication-of-the-irr-for-the-new-government-procurement-act/), approved 4 February and published 10 February 2025.
- DBM ICTSS, [eBudget user helpdesk](https://ictsshelpdesk.dbm.gov.ph/support/solutions/articles/159000412716-how-to-enable-and-use-ie-mode-compatibility-in-edge-browser), updated 24 September 2025.
- COA Government Accountancy Sector, [AFRS, eNGAS and eBudget](https://gas.coa.gov.ph/GASWebsite/).
- DBM, [UACS Joint Circular 2013-1](https://www.dbm.gov.ph/index.php/central-office?catid=61&id=3236&view=article) and [UACS administration](https://www.dbm.gov.ph/index.php?catid=277&id=1628%3Aissuance-of-unified-accounts-code-structure-uacs&view=article).
- Bureau of the Treasury, [Government Accounting Manual, volume I](https://www.treasury.gov.ph/wp-content/uploads/2018/01/Volume-I.pdf), permissible disbursement modes.

## How to read evidence

`model/sources.csv` records where a claim is drawn from, and a source's *type*, not an independent correctness certificate. `model/flows.csv` separately codes implementation **stage**. The audit register adds reviewer judgement using the categories `corroborated`, `qualified`, `needs_evidence`, `model_inference`; one review attaches to a **qualified proposition**, not to every assertion about a system. `needs_evidence` does not mean the system does not exist. `not_stated` does not mean a connection does not exist.

A source may be useful without establishing actual integration, current deployment, internal schema, performance, or compliance. The atlas extraction includes historical and derived claims; those should be confirmed against the cited primary documents before being asserted as definitive. Figures and statements could change after this review date. This edition retains unresolved cases deliberately rather than inventing links.

## Technical model limitations

- Graphviz arrows represent registered relationships and carriers, not a tested network of APIs. Diagram proximity never implies connectivity.
- PNML contains ordinary place/transition nets; read arcs are represented as input/output pairs. A monetary `amount` annotation in the CSV is **not** a numeric token weight in PNML. The chain nets therefore cannot establish cash invariants, UACS consistency, eligibility, calendar deadlines, or lawful disbursement amounts.
- Finite-state soundness refers only to the **generated sequence nets**, not all curated chain nets. It is not a validation of data accuracy or live transaction systems.
- ICONIX robustness checks test diagram-link categories, not the truth of actors' assignments or accuracy of the underlying legal process.
- Source URLs are not checked continuously. The automatic audit verifies referential integrity and reproducibility, **not the truth of online source content**.

See `REPRODUCIBILITY.md` for verifiable commands and tests. To add further independently reviewed claims, append a source-linked, dated row to `audit/claim_reviews.csv` and rebuild.
