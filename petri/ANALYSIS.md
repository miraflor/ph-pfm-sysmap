# Analysis of the process nets

This file is written by tools/build.py. Do not edit it by hand.

## Curated chain nets

One net for each chain and cohort. A place with no input is where the chain starts (a source); a place with no output is where it ends (a sink). A read arc needs a token and leaves it. In PNML a read arc is written as two arcs, one in each direction.

| Net | Chain | Places | Transitions | Arcs | Read arcs | Sources | Sinks |
|---|---|---|---|---|---|---|---|
| CH-SPEND-P | Spending: from an allotment to a settled payment and its records | 40 | 23 | 75 | 4 | S-TSA, S-ALLOT, S-AWARD, S-MONTH-END | S-PAYABLE, S-ORS-PAYABLE, C-F018, S-SETTLED, C-F040, C-F035, S-ORS-PAID, S-AUDITED, S-RECONCILED |
| CH-SPEND-E | Spending: from an allotment to a settled payment and its records | 40 | 23 | 75 | 4 | S-TSA, S-ALLOT, S-AWARD, S-MONTH-END | S-PAYABLE, S-ORS-PAYABLE, C-F018, S-SETTLED, C-F040, C-F035, S-ORS-PAID, S-AUDITED, S-RECONCILED |
| CH-SPEND-B | Spending: from an allotment to a settled payment and its records | 24 | 13 | 43 | 3 | S-TSA, S-ALLOT, S-AWARD | S-ORS-PAID, C-F127, S-SETTLED, S-RECONCILED |
| CH-RELEASE-P | Release of allotments | 11 | 10 | 23 | 1 | S-NBC, S-APPROP | S-ALLOT, S-VERIFIABLE |
| CH-RELEASE-E | Release of allotments | 11 | 10 | 23 | 1 | S-NBC, S-APPROP | S-ALLOT, S-VERIFIABLE |
| CH-RELEASE-B | Release of allotments | 11 | 10 | 23 | 1 | S-NBC, S-APPROP | S-ALLOT, S-VERIFIABLE |
| CH-PROC-P | Procurement in PhilGEPS up to the award | 8 | 5 | 13 | 2 | S-NEED | C-F041, C-F103, S-AWARD, C-F013-NOA |
| CH-PROC-E | Procurement in PhilGEPS up to the award | 8 | 5 | 13 | 2 | S-NEED | C-F041, C-F103, S-AWARD, C-F013-NOA |
| CH-PROC-B | Procurement in PhilGEPS up to the award | 9 | 6 | 15 | 2 | S-NEED | C-F041, C-F103, S-AWARD, C-F026 |
| CH-COLLECT-P | Collections of an agency to the Treasury | 14 | 10 | 24 | 0 | S-FEE-DUE | C-F052, C-F054, C-F055 |
| CH-COLLECT-E | Collections of an agency to the Treasury | 14 | 10 | 24 | 0 | S-FEE-DUE | C-F052, C-F054, C-F055 |
| CH-COLLECT-B | Collections of an agency to the Treasury | 13 | 9 | 22 | 0 | S-FEE-DUE | S-JEV-COLL, C-F052, C-F054 |
| CH-TAX-P | Tax and customs collections | 16 | 12 | 28 | 0 | S-TAX-DUE, S-IMPORT | S-TAX-POSTED, S-TSA, S-RELEASED |
| CH-TAX-E | Tax and customs collections | 16 | 12 | 28 | 0 | S-TAX-DUE, S-IMPORT | S-TAX-POSTED, S-TSA, S-RELEASED |
| CH-TAX-B | Tax and customs collections | 16 | 12 | 28 | 0 | S-TAX-DUE, S-IMPORT | S-TAX-POSTED, S-TSA, S-RELEASED |
| CH-DEBT-P | Borrowing through government securities | 10 | 6 | 16 | 1 | S-FIN-NEED, S-DEBT-DUE | C-F059, C-F060 |
| CH-DEBT-E | Borrowing through government securities | 10 | 6 | 16 | 1 | S-FIN-NEED, S-DEBT-DUE | C-F059, C-F060 |
| CH-DEBT-B | Borrowing through government securities | 10 | 6 | 16 | 1 | S-FIN-NEED, S-DEBT-DUE | C-F059, C-F060 |
| CH-REPORT-P | Reporting | 10 | 6 | 15 | 4 | S-ORS-PAID, S-JEV-PAID | C-F021A, C-F021B, C-F021C, S-AFR, C-F031 |
| CH-REPORT-E | Reporting | 10 | 6 | 15 | 4 | S-ORS-PAID, S-JEV-PAID | C-F021A, C-F021B, C-F021C, S-AFR, C-F031 |
| CH-REPORT-B | Reporting | 10 | 6 | 16 | 5 | S-JEV-PAID, S-ORS-PAID | C-F124, C-F125, C-F126, S-AFR, C-F031 |
| CH-PLAN-P | From the investment program to the enacted budget in the systems | 13 | 8 | 22 | 1 | S-PIP-CALL, S-BUDGET-CALL, S-POSITIONS | S-APPROP |
| CH-PLAN-E | From the investment program to the enacted budget in the systems | 13 | 8 | 22 | 1 | S-PIP-CALL, S-BUDGET-CALL, S-POSITIONS | S-APPROP |
| CH-PLAN-B | From the investment program to the enacted budget in the systems | 13 | 8 | 22 | 1 | S-PIP-CALL, S-BUDGET-CALL, S-POSITIONS | S-APPROP |
| CH-ALL-P | All chains together | 115 | 80 | 216 | 13 | S-MONTH-END, S-NBC, S-NEED, S-FEE-DUE, S-TAX-DUE, S-IMPORT, S-FIN-NEED, S-DEBT-DUE, S-PIP-CALL, S-BUDGET-CALL, S-POSITIONS | S-PAYABLE, S-ORS-PAYABLE, C-F018, S-SETTLED, C-F040, C-F035, S-AUDITED, S-RECONCILED, S-VERIFIABLE, C-F041, C-F103, C-F013-NOA, C-F052, C-F054, C-F055, S-TAX-POSTED, S-RELEASED, C-F059, C-F060, C-F021A, C-F021B, C-F021C, S-AFR, C-F031 |
| CH-ALL-E | All chains together | 115 | 80 | 216 | 13 | S-MONTH-END, S-NBC, S-NEED, S-FEE-DUE, S-TAX-DUE, S-IMPORT, S-FIN-NEED, S-DEBT-DUE, S-PIP-CALL, S-BUDGET-CALL, S-POSITIONS | S-PAYABLE, S-ORS-PAYABLE, C-F018, S-SETTLED, C-F040, C-F035, S-AUDITED, S-RECONCILED, S-VERIFIABLE, C-F041, C-F103, C-F013-NOA, C-F052, C-F054, C-F055, S-TAX-POSTED, S-RELEASED, C-F059, C-F060, C-F021A, C-F021B, C-F021C, S-AFR, C-F031 |
| CH-ALL-B | All chains together | 99 | 70 | 185 | 13 | S-NBC, S-NEED, S-FEE-DUE, S-TAX-DUE, S-IMPORT, S-FIN-NEED, S-DEBT-DUE, S-PIP-CALL, S-BUDGET-CALL, S-POSITIONS | C-F127, S-SETTLED, S-RECONCILED, S-VERIFIABLE, C-F041, C-F103, C-F026, S-JEV-COLL, C-F052, C-F054, S-TAX-POSTED, S-RELEASED, C-F059, C-F060, C-F124, C-F125, C-F126, S-AFR, C-F031 |

## Windows in which the NCA balances differ

Rule R-NCA-EQUAL is a reconciliation objective, not a claim of identical balances at every moment. The listed transitions touch some but not all of the corresponding record places. That structural observation identifies possible timing differences, not measured monetary discrepancies or proof that a real reconciliation succeeds. The rule is a modelling inference; these ordinary PT nets do not encode monetary values or UACS dimensions.

### Cohort B: 2 places (S-NCA-AGENCY, S-NCA-BANK)

- SP-02 Credit the NCA to the MDS sub-account: changes S-NCA-BANK only
- SP-03 Record the NCA received: changes S-NCA-AGENCY only
- SP-10 Certify cash available and approve: changes S-NCA-AGENCY only
- SP-13C Debit the sub-account and pass the transfer to the clearing house: changes S-NCA-BANK only

### Cohort E: 3 places (S-NCA-AGENCY, S-NCA-CASH, S-NCA-BANK)

- SP-02 Credit the NCA to the MDS sub-account: changes S-NCA-BANK only
- SP-03 Record the NCA received: changes S-NCA-AGENCY, S-NCA-CASH only
- SP-10 Certify cash available and approve: changes S-NCA-AGENCY only
- SP-11 Prepare and sign the payment order: changes S-NCA-CASH only
- SP-13A Check and pay the paper order: changes S-NCA-BANK only
- SP-13B Check and pay the eMDS order: changes S-NCA-BANK only

### Cohort P: 3 places (S-NCA-AGENCY, S-NCA-CASH, S-NCA-BANK)

- SP-02 Credit the NCA to the MDS sub-account: changes S-NCA-BANK only
- SP-03 Record the NCA received: changes S-NCA-AGENCY, S-NCA-CASH only
- SP-10 Certify cash available and approve: changes S-NCA-AGENCY only
- SP-11 Prepare and sign the payment order: changes S-NCA-CASH only
- SP-13A Check and pay the paper order: changes S-NCA-BANK only
- SP-13B Check and pay the eMDS order: changes S-NCA-BANK only

## Workflow nets of the atlas sequence diagrams

Each sequence diagram of the atlas is turned into a workflow net: one start place, one end place, a transition for each message or own action, and silent transitions for the blocks (alt is an exclusive choice, opt is a choice with a silent skip, par is a split and a join, loop is repeat or exit). Blocks of the kind break, critical and rect are taken in sequence. The check searches all reachable markings. A net is sound when every reachable marking can reach the end, the end is reached with no other token left, every transition can fire, and no place ever holds two tokens.

| Diagram | Title | Steps | Silent | Places | Markings | Sound |
|---|---|---|---|---|---|---|
| 01b | Investment programming: how a project enters the PIP and TRIP and reaches the budget | 15 | 2 | 17 | 17 | yes |
| 03a | Budget preparation: from the fiscal program to the President's budget (example: FY 2027 budget, prepared in 2026) | 19 | 2 | 23 | 26 | yes |
| 04a | Budget legislation: from the President's budget to the General Appropriations Act (GAA) | 21 | 4 | 26 | 29 | yes |
| 05a | Release of funds: two separate authorities, allotment (to commit) and cash authority (to pay). Example: FY 2026 | 19 | 6 | 23 | 23 | yes |
| 06b | Competitive bidding under the New Government Procurement Act (RA 12009): who does what, with the time limits | 22 | 5 | 26 | 26 | yes |
| 07a | From obligation to payment: who certifies what, and which record each step writes (goods bought by a national agency, paid by payment order) | 32 | 0 | 33 | 33 | yes |
| 07d | Payment and settlement: how money moves from the Treasury Single Account to the payee (Modified Disbursement System) | 13 | 2 | 15 | 15 | yes |
| 07i | A works contract with an advance, progress billings and retention money (example of the Manual) | 15 | 0 | 16 | 16 | yes |
| 09a | External audit by COA: from submission of accounts to the annual reports | 18 | 5 | 21 | 21 | yes |
| 10b | Collection of taxes and customs duties: from the taxpayer to the Treasury Single Account | 16 | 0 | 17 | 17 | yes |
| 10d | A tax refund: how money collected as tax is paid back | 11 | 0 | 12 | 12 | yes |
| 11b | Cash programming: how the amount of cash authority for a period is decided | 17 | 7 | 22 | 22 | yes |
| 11d | One foreign project loan: approvals, signing, use of the loan and repayment | 21 | 2 | 23 | 23 | yes |
| 12a | Personnel spending: from an authorized position to the monthly payroll and the remittances | 16 | 2 | 18 | 18 | yes |
| 14a | Budget cycle of a local government unit (province, city or municipality) under the Local Government Code | 19 | 3 | 22 | 22 | yes |
| 14f | The budget of a barangay: who prepares, who enacts, who reviews | 11 | 2 | 13 | 13 | yes |
| 15a | Government corporations (GOCCs): corporate operating budget, budgetary support and reports | 17 | 2 | 19 | 19 | yes |
| 15b | Transfer of funds from one agency to another body that will implement | 13 | 2 | 15 | 15 | yes |
| 15f | Cash aid to persons: from the list of beneficiaries to the credit in each account | 12 | 0 | 13 | 13 | yes |
| 16f | Public verification of DBM release documents with a blockchain record | 9 | 0 | 10 | 10 | yes |
