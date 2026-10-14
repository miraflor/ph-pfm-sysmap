# ICONIX use cases

This file is written by tools/build.py from model/use_cases.csv, model/transitions.csv, model/bindings.csv and the sequence diagrams of the atlas. Do not edit it by hand.

There are two kinds of use case here.

System use cases follow the curated chains of the process nets. Each one is a group of transitions with one goal. It is written once for each group of cohorts in which the same acts happen through the same boundary and control objects. The boundary object is what the actor touches (a form, a screen, a portal). The control object is the check of the step, done by a person, by software or by the bank. The entity objects are the records that the step uses or writes, with the body or system that holds them in that cohort.

Business use cases are made from the twenty sequence diagrams of the atlas. Their basic course is the first branch of every choice; the other branches and the optional blocks are the alternate courses.

## System use cases

### UC-SP-1 Receive the cash authority (NCA)

Chain: CH-SPEND (Spending: from an allotment to a settled payment and its records). Primary actor: Chief accountant (head of the accounting unit).

Goal: The agency knows how much it may pay this month, and the bank holds the same limit.

Basic course in cohort P (diagrams: robustness/UC-SP-1_P, sequence/UC-SP-1_P):

1. DBM (bureaus and approving officials): Issue the NCA (SP-01). Boundary: NCA prepared by DBM; advice of NCA issued in ADRS. Control: DBM approving official, a person checks. Writes in: e-Budget (DBM), ADRS. Records: Budget Execution Documents: BED 1 Financial Plan, BED 2 Physical Plan, BED 3 Monthly Disbursement Program [URS: Budget execution documents]; Notice of Cash Allocation (NCA); Advice of NCA Issued.
2. Servicing bank: Credit the NCA to the MDS sub-account (SP-02). Boundary: Records of the bank. Control: Servicing bank, the bank checks. Writes in: MDS sub-accounts. Records: Notice of Cash Allocation (NCA).
3. Chief accountant (head of the accounting unit): Record the NCA received (SP-03). Boundary: Paper forms: journal entry voucher, registry of the NCA. Control: Chief accountant, a person checks. Writes in: Agency own systems. Records: Advice of NCA Issued; RANCA, Registry of Allotments and Notice of Cash Allocation, App.30 [Agency own systems]; Checks and ADA Disbursements Record, App.34 [Agency own systems].

Basic course in cohort E (diagrams: robustness/UC-SP-1_E, sequence/UC-SP-1_E):

1. DBM (bureaus and approving officials): Issue the NCA (SP-01). Boundary: NCA prepared by DBM; advice of NCA issued in ADRS. Control: DBM approving official, a person checks. Writes in: e-Budget (DBM), ADRS. Records: Budget Execution Documents: BED 1 Financial Plan, BED 2 Physical Plan, BED 3 Monthly Disbursement Program [URS: Budget execution documents]; Notice of Cash Allocation (NCA); Advice of NCA Issued.
2. Servicing bank: Credit the NCA to the MDS sub-account (SP-02). Boundary: Records of the bank. Control: Servicing bank, the bank checks. Writes in: MDS sub-accounts. Records: Notice of Cash Allocation (NCA).
3. Chief accountant (head of the accounting unit): Record the NCA received (SP-03). Boundary: eNGAS for the journal entry; registry of the NCA kept by the accounting unit. Control: Chief accountant, a person checks. Writes in: eNGAS, Agency own systems. Records: Advice of NCA Issued; RANCA, Registry of Allotments and Notice of Cash Allocation, App.30 [Agency own systems]; Checks and ADA Disbursements Record, App.34 [Agency own systems].

Basic course in cohort B (diagrams: robustness/UC-SP-1_B, sequence/UC-SP-1_B):

1. DBM (bureaus and approving officials): Issue the NCA (SP-01). Boundary: NCA prepared by DBM; advice of NCA issued in ADRS. Control: DBM approving official, a person checks. Writes in: e-Budget (DBM), ADRS. Records: Budget Execution Documents: BED 1 Financial Plan, BED 2 Physical Plan, BED 3 Monthly Disbursement Program [URS: Budget execution documents]; Notice of Cash Allocation (NCA); Advice of NCA Issued.
2. Servicing bank: Credit the NCA to the MDS sub-account (SP-02). Boundary: Records of the bank. Control: Servicing bank, the bank checks. Writes in: MDS sub-accounts. Records: Notice of Cash Allocation (NCA).
3. Chief accountant (head of the accounting unit): Record the NCA received (SP-03). Boundary: BTMS: the NCA is loaded into the system. Control: BTMS, software checks. Writes in: BTMS. Records: Advice of NCA Issued; RANCA, Registry of Allotments and Notice of Cash Allocation, App.30 [BTMS].

Alternate courses:

- If the cash need is above the program, the agency asks for an additional NCA (diagram 05a, optional block) [NBC599]
- An unused regular NCA lapses on the last working day of the quarter [NBC599]

### UC-SP-2 Obligate and contract

Chain: CH-SPEND (Spending: from an allotment to a settled payment and its records). Primary actor: Head of the budget unit.

Goal: An obligation is recorded against the allotment, and the contract or purchase order is in force.

Basic course in cohort P (diagrams: robustness/UC-SP-2_P, sequence/UC-SP-2_P):

1. Head of the budget unit: Obligate and sign the contract (SP-05). Boundary: Paper forms: ORS (Box A, Box B), purchase order with the certificate of funds available. Control: Head of the budget unit (Box B) and chief accountant (funds available), a person checks. Writes in: Agency own systems. Records: Special Allotment Release Order (SARO) [Agency own systems]; GAA as allotment order (GAAAO) [Agency own systems]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [Agency own systems]; Notice of award [PhilGEPS (modernized)]; Resolution of the BAC recommending award [PhilGEPS (modernized)]; Obligation Request and Status (ORS), App.11 [Agency own systems]; Contract or Purchase Order, App.61 [Agency own systems].

Basic course in cohort E (diagrams: robustness/UC-SP-2_E, sequence/UC-SP-2_E):

1. Head of the budget unit: Obligate and sign the contract (SP-05). Boundary: eBudget of COA for the registry; paper ORS and purchase order. Control: Head of the budget unit and chief accountant, a person checks. Writes in: eBudget (COA). Records: Special Allotment Release Order (SARO) [eBudget (COA)]; GAA as allotment order (GAAAO) [eBudget (COA)]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [eBudget (COA)]; Notice of award [PhilGEPS (modernized)]; Resolution of the BAC recommending award [PhilGEPS (modernized)]; Obligation Request and Status (ORS), App.11 [eBudget (COA)]; Contract or Purchase Order, App.61 [Agency own systems].

Basic course in cohort B (diagrams: robustness/UC-SP-2_B, sequence/UC-SP-2_B):

1. Head of the budget unit: Obligate and sign the contract (SP-05). Boundary: BTMS: purchase request, commitment, purchase order and obligation request. Control: BTMS blocks commitments and obligations above the allotment, software checks. Writes in: BTMS: 1 Commitment and obligations. Records: Special Allotment Release Order (SARO) [BTMS: 1 Commitment and obligations]; GAA as allotment order (GAAAO) [BTMS: 1 Commitment and obligations]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [BTMS: 1 Commitment and obligations]; Notice of award [PhilGEPS (modernized)]; Resolution of the BAC recommending award [PhilGEPS (modernized)]; Obligation Request and Status (ORS), App.11 [BTMS: 1 Commitment and obligations]; Contract or Purchase Order, App.61 [BTMS: 1 Commitment and obligations].

Alternate courses:

- If the allotment available is not enough, the head of the budget unit does not sign Box B (cohorts P and E), or BTMS blocks the obligation (cohort B) [GAM-V1 Ch.3 s.15][BTMS-SITE]

### UC-SP-3 Accept the delivery and record the payable

Chain: CH-SPEND (Spending: from an allotment to a settled payment and its records). Primary actor: Inspection officer and property custodian.

Goal: The delivery is inspected and accepted, and the payable is in the books.

Basic course in cohort P (diagrams: robustness/UC-SP-3_P, sequence/UC-SP-3_P):

1. Supplier or contractor: Deliver (SP-06). Boundary: Delivery receipt and invoice of the supplier. Control: Supplier, a person checks. Records: Contract or Purchase Order, App.61 [Agency own systems]; Delivery receipt; Invoice, billing, statement of work accomplished.
2. Inspection officer and property custodian: Inspect and accept (SP-07). Boundary: Paper form: inspection and acceptance report. Control: Inspection officer and property custodian, a person checks. Writes in: Agency own systems. Records: Delivery receipt; Invoice, billing, statement of work accomplished; Inspection and Acceptance Report (IAR), App.62 [Agency own systems]; Contract or Purchase Order, App.61.
3. Chief accountant (head of the accounting unit): Record the payable (SP-08). Boundary: Paper form: journal entry voucher. Control: Chief accountant, a person checks. Writes in: Agency own systems. Records: Inspection and Acceptance Report (IAR), App.62; Contract or Purchase Order, App.61; Delivery receipt; Journal Entry Voucher (JEV), App.36 [Agency own systems].
4. Head of the budget unit: Post the payable in part C of the ORS (SP-08B). Boundary: Paper ORS, part C. Control: Head of the budget unit, a person checks. Writes in: Agency own systems. Records: Journal Entry Voucher (JEV), App.36; Obligation Request and Status (ORS), App.11 [Agency own systems].

Basic course in cohort E (diagrams: robustness/UC-SP-3_E, sequence/UC-SP-3_E):

1. Supplier or contractor: Deliver (SP-06). Boundary: Delivery receipt and invoice of the supplier. Control: Supplier, a person checks. Records: Contract or Purchase Order, App.61 [Agency own systems]; Delivery receipt; Invoice, billing, statement of work accomplished.
2. Inspection officer and property custodian: Inspect and accept (SP-07). Boundary: Paper form: inspection and acceptance report. Control: Inspection officer and property custodian, a person checks. Writes in: Agency own systems. Records: Delivery receipt; Invoice, billing, statement of work accomplished; Inspection and Acceptance Report (IAR), App.62 [Agency own systems]; Contract or Purchase Order, App.61.
3. Chief accountant (head of the accounting unit): Record the payable (SP-08). Boundary: eNGAS: journal entry. Control: Chief accountant, a person checks. Writes in: eNGAS. Records: Inspection and Acceptance Report (IAR), App.62; Contract or Purchase Order, App.61; Delivery receipt; Journal Entry Voucher (JEV), App.36 [eNGAS].
4. Head of the budget unit: Post the payable in part C of the ORS (SP-08B). Boundary: eBudget of COA. Control: Head of the budget unit, a person checks. Writes in: eBudget (COA). Records: Journal Entry Voucher (JEV), App.36; Obligation Request and Status (ORS), App.11 [eBudget (COA)].

Basic course in cohort B (diagrams: robustness/UC-SP-3_B, sequence/UC-SP-3_B):

1. Supplier or contractor: Deliver (SP-06). Boundary: Delivery receipt and invoice of the supplier. Control: Supplier, a person checks. Records: Contract or Purchase Order, App.61 [BTMS: 1 Commitment and obligations]; Delivery receipt; Invoice, billing, statement of work accomplished.
2. Inspection officer and property custodian: Inspect and accept (SP-07). Boundary: BTMS: goods received note (and goods return note). Control: Inspection officer and property custodian; the system matches the note with the purchase order, a person checks. Writes in: BTMS: 2 Payments. Records: Delivery receipt; Invoice, billing, statement of work accomplished; Inspection and Acceptance Report (IAR), App.62 [BTMS: 2 Payments].

Alternate courses:

- A partial delivery is recorded as partial on the acceptance report [GAM-V2 App.62]
- For a lawful advance, a security replaces the accepted delivery (atlas diagram 00d, t4b) [IRR12009 s.71.2.5]
- Goods returned: goods return note in BTMS (cohort B) [CL2025-8]

### UC-SP-4 Examine and approve the claim

Chain: CH-SPEND (Spending: from an allotment to a settled payment and its records). Primary actor: Chief accountant (head of the accounting unit).

Goal: The voucher is certified and approved for payment within the cash authority.

Basic course in cohort P (diagrams: robustness/UC-SP-4_P, sequence/UC-SP-4_P):

1. Chief accountant (head of the accounting unit): Prepare and examine the claim (SP-09). Boundary: Paper forms: disbursement voucher (Box A, Box B), index of payments. Control: Accounting staff check against a list, the ORS and the index of payments, a person checks. Writes in: Agency own systems. Records: Obligation Request and Status (ORS), App.11 [Agency own systems]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [Agency own systems]; Inspection and Acceptance Report (IAR), App.62 [Agency own systems]; Disbursement Voucher (DV), App.32 [Agency own systems]; Index of Payments, App.38 [Agency own systems].
2. Chief accountant (head of the accounting unit): Certify cash available and approve (SP-10). Boundary: Paper voucher, Box C and Box D; registry of the NCA. Control: Chief accountant reads the registry of the NCA, a person checks. Writes in: Agency own systems. Records: Disbursement Voucher (DV), App.32 [Agency own systems]; Index of Payments, App.38 [Agency own systems]; RANCA, Registry of Allotments and Notice of Cash Allocation, App.30 [Agency own systems].

Basic course in cohort E (diagrams: robustness/UC-SP-4_E, sequence/UC-SP-4_E):

1. Chief accountant (head of the accounting unit): Prepare and examine the claim (SP-09). Boundary: Paper voucher; the obligation is looked up in the eBudget of COA. Control: Accounting staff, a person checks. Writes in: Agency own systems. Records: Obligation Request and Status (ORS), App.11 [eBudget (COA)]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [eBudget (COA)]; Inspection and Acceptance Report (IAR), App.62 [Agency own systems]; Disbursement Voucher (DV), App.32 [Agency own systems]; Index of Payments, App.38 [Agency own systems].
2. Chief accountant (head of the accounting unit): Certify cash available and approve (SP-10). Boundary: Paper voucher, Box C and Box D; registry of the NCA. Control: Chief accountant reads the registry of the NCA, a person checks. Writes in: Agency own systems. Records: Disbursement Voucher (DV), App.32 [Agency own systems]; Index of Payments, App.38 [Agency own systems]; RANCA, Registry of Allotments and Notice of Cash Allocation, App.30 [Agency own systems].

Basic course in cohort B (diagrams: robustness/UC-SP-4_B, sequence/UC-SP-4_B):

1. Chief accountant (head of the accounting unit): Prepare and examine the claim (SP-09). Boundary: BTMS: disbursement voucher linked to an approved ORS, matched with the purchase order and goods received note. Control: BTMS links and matches; accounting staff examine, software checks. Writes in: BTMS: 2 Payments. Records: Obligation Request and Status (ORS), App.11 [BTMS: 1 Commitment and obligations]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [BTMS: 1 Commitment and obligations]; Inspection and Acceptance Report (IAR), App.62 [BTMS: 2 Payments]; Disbursement Voucher (DV), App.32 [BTMS: 2 Payments]; Index of Payments, App.38 [BTMS: 2 Payments].
2. Chief accountant (head of the accounting unit): Certify cash available and approve (SP-10). Boundary: BTMS: approval of the voucher. Control: BTMS enforces the limits of the cash allocation and of the bank balance, software checks. Writes in: BTMS: 2 Payments. Records: Disbursement Voucher (DV), App.32 [BTMS: 2 Payments]; Index of Payments, App.38 [BTMS: 2 Payments]; RANCA, Registry of Allotments and Notice of Cash Allocation, App.30 [BTMS].

Alternate courses:

- If the NCA balance is not enough, the voucher is kept until cash is available [GAM-V1 Ch.6 s.12]
- If a supporting document is missing, Box C (documents complete) is not certified [GAM-V2 App.32]

### UC-SP-5 Pay the payee

Chain: CH-SPEND (Spending: from an allotment to a settled payment and its records). Primary actor: Cashier or disbursing officer.

Goal: The payee is credited, and the bank is replenished from the Treasury Single Account.

Basic course in cohort P (diagrams: robustness/UC-SP-5_P, sequence/UC-SP-5_P):

1. Cashier or disbursing officer: Prepare and sign the payment order (SP-11). Boundary: Paper forms: LDDAP-ADA in five copies, summary list (SLIIE), record of checks and payment orders. Control: Chief accountant, head of agency and cashier sign, a person checks. Writes in: Agency own systems. Records: Disbursement Voucher (DV), App.32 [Agency own systems]; Checks and ADA Disbursements Record, App.34 [Agency own systems]; List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42 [Agency own systems]; Summary of LDDAP-ADAs Issued and Invalidated ADA Entries (SLIIE), App.53 [Agency own systems].
2. Cashier or disbursing officer: Send the payment order on paper (SP-12A). Boundary: Signed paper copies delivered to the bank. Control: Cashier, a person checks. Records: List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42 [Agency own systems]; Summary of LDDAP-ADAs Issued and Invalidated ADA Entries (SLIIE), App.53 [Agency own systems]; Checks and ADA Disbursements Record, App.34 [Agency own systems].
3. Cashier or disbursing officer: Send the payment order through eMDS (SP-12B). Boundary: eMDS internet banking facility of the Land Bank. Control: Cashier, a person checks. Writes in: eMDS (Land Bank). Records: List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42 [Agency own systems]; Summary of LDDAP-ADAs Issued and Invalidated ADA Entries (SLIIE), App.53 [Agency own systems]; Checks and ADA Disbursements Record, App.34 [Agency own systems].
4. Servicing bank: Check and pay the paper order (SP-13A). Boundary: Records of the bank. Control: Servicing bank checks account details (and the NCA balance), the bank checks. Writes in: MDS sub-accounts. Records: List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42; Summary of LDDAP-ADAs Issued and Invalidated ADA Entries (SLIIE), App.53; Notice of Cash Allocation (NCA) [MDS sub-accounts]; Credit to the account of a payee (money); Report of payments made by a servicing bank [Servicing banks].
5. Servicing bank: Check and pay the eMDS order (SP-13B). Boundary: eMDS and records of the bank. Control: Servicing bank, the bank checks. Writes in: MDS sub-accounts. Records: List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42; Notice of Cash Allocation (NCA) [MDS sub-accounts]; Credit to the account of a payee (money); Report of payments made by a servicing bank [Servicing banks].
6. Bureau of the Treasury: Replenish the servicing bank (SP-14). Boundary: Report of payments in eTRAMS; paper copies (cohorts P and E); instruction to the BSP. Control: BTr, a person checks. Writes in: eTRAMS, BTr NGAS (books). Records: Report of payments made by a servicing bank [Servicing banks]; Replenishment of a servicing bank from the Treasury Single Account (money); Summary of LDDAP-ADAs Issued and Invalidated ADA Entries (SLIIE), App.53; List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42.
7. Servicing bank: Receive the replenishment (SP-15). Boundary: Records of the bank at the BSP. Control: BSP and the bank, the bank checks. Writes in: MDS sub-accounts. Records: Replenishment of a servicing bank from the Treasury Single Account (money).

Basic course in cohort E (diagrams: robustness/UC-SP-5_E, sequence/UC-SP-5_E):

1. Cashier or disbursing officer: Prepare and sign the payment order (SP-11). Boundary: Paper forms: LDDAP-ADA, summary list, record of checks and payment orders. Control: Chief accountant, head of agency and cashier sign, a person checks. Writes in: Agency own systems. Records: Disbursement Voucher (DV), App.32 [Agency own systems]; Checks and ADA Disbursements Record, App.34 [Agency own systems]; List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42 [Agency own systems]; Summary of LDDAP-ADAs Issued and Invalidated ADA Entries (SLIIE), App.53 [Agency own systems].
2. Cashier or disbursing officer: Send the payment order on paper (SP-12A). Boundary: Signed paper copies delivered to the bank. Control: Cashier, a person checks. Records: List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42 [Agency own systems]; Summary of LDDAP-ADAs Issued and Invalidated ADA Entries (SLIIE), App.53 [Agency own systems]; Checks and ADA Disbursements Record, App.34 [Agency own systems].
3. Cashier or disbursing officer: Send the payment order through eMDS (SP-12B). Boundary: eMDS internet banking facility of the Land Bank. Control: Cashier, a person checks. Writes in: eMDS (Land Bank). Records: List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42 [Agency own systems]; Summary of LDDAP-ADAs Issued and Invalidated ADA Entries (SLIIE), App.53 [Agency own systems]; Checks and ADA Disbursements Record, App.34 [Agency own systems].
4. Servicing bank: Check and pay the paper order (SP-13A). Boundary: Records of the bank. Control: Servicing bank checks account details (and the NCA balance), the bank checks. Writes in: MDS sub-accounts. Records: List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42; Summary of LDDAP-ADAs Issued and Invalidated ADA Entries (SLIIE), App.53; Notice of Cash Allocation (NCA) [MDS sub-accounts]; Credit to the account of a payee (money); Report of payments made by a servicing bank [Servicing banks].
5. Servicing bank: Check and pay the eMDS order (SP-13B). Boundary: eMDS and records of the bank. Control: Servicing bank, the bank checks. Writes in: MDS sub-accounts. Records: List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42; Notice of Cash Allocation (NCA) [MDS sub-accounts]; Credit to the account of a payee (money); Report of payments made by a servicing bank [Servicing banks].
6. Bureau of the Treasury: Replenish the servicing bank (SP-14). Boundary: Report of payments in eTRAMS; paper copies (cohorts P and E); instruction to the BSP. Control: BTr, a person checks. Writes in: eTRAMS, BTr NGAS (books). Records: Report of payments made by a servicing bank [Servicing banks]; Replenishment of a servicing bank from the Treasury Single Account (money); Summary of LDDAP-ADAs Issued and Invalidated ADA Entries (SLIIE), App.53; List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42.
7. Servicing bank: Receive the replenishment (SP-15). Boundary: Records of the bank at the BSP. Control: BSP and the bank, the bank checks. Writes in: MDS sub-accounts. Records: Replenishment of a servicing bank from the Treasury Single Account (money).

Basic course in cohort B (diagrams: robustness/UC-SP-5_B, sequence/UC-SP-5_B):

1. Cashier or disbursing officer: Pay through BTMS (SP-12C). Boundary: BTMS: payment by electronic funds transfer, payment extract. Control: BTMS, software checks. Writes in: BTMS: 2 Payments, BTMS: 5 Accounting and reporting. Records: Disbursement Voucher (DV), App.32 [BTMS: 2 Payments]; Instruction for an electronic payment (credit transfer); Journal Entry Voucher (JEV), App.36 [BTMS: 5 Accounting and reporting]; Obligation Request and Status (ORS), App.11 [BTMS]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [BTMS].
2. Servicing bank: Debit the sub-account and pass the transfer to the clearing house (SP-13C). Boundary: Records of the bank; ISO 20022 messages to PESONet or InstaPay. Control: Servicing bank, the bank checks. Writes in: MDS sub-accounts. Records: Instruction for an electronic payment (credit transfer); Notice of Cash Allocation (NCA) [MDS sub-accounts]; Credit to the account of a payee (money); Report of payments made by a servicing bank [Servicing banks]; Electronic bank statement.
3. Bureau of the Treasury: Replenish the servicing bank (SP-14). Boundary: Report of payments in eTRAMS; paper copies (cohorts P and E); instruction to the BSP. Control: BTr, a person checks. Writes in: eTRAMS, BTr NGAS (books). Records: Report of payments made by a servicing bank [Servicing banks]; Replenishment of a servicing bank from the Treasury Single Account (money).
4. Servicing bank: Receive the replenishment (SP-15). Boundary: Records of the bank at the BSP. Control: BSP and the bank, the bank checks. Writes in: MDS sub-accounts. Records: Replenishment of a servicing bank from the Treasury Single Account (money).

Alternate courses:

- If the bank cannot credit an item because branch, account name or number do not agree, the entry is invalidated; the agency reverses its entry, lists it in the next summary list and issues a new payment order [GAM-V1 Ch.6 s.54, ss.44-45]
- Payment by MDS check with the advice of checks issued and cancelled [GAM-V2 App.39]
- Agencies with sub-accounts at the Land Bank may send the order through eMDS [eMDS]

### UC-SP-6 Record, report and audit the payment

Chain: CH-SPEND (Spending: from an allotment to a settled payment and its records). Primary actor: Chief accountant (head of the accounting unit).

Goal: The payment is in the books and registries, the taxes withheld are remitted, and the auditor has the paid documents.

Basic course in cohort P (diagrams: robustness/UC-SP-6_P, sequence/UC-SP-6_P):

1. Cashier or disbursing officer: Receive the validated copy and prepare the daily report (SP-16). Boundary: Paper forms: validated LDDAP-ADA, official receipt of the payee, report of ADA issued (RADAI). Control: Cashier, a person checks. Writes in: Agency own systems. Records: List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42; Report of Checks Issued (RCI), App.35, and Report of ADA Issued (RADAI), App.13; Disbursement Voucher (DV), App.32.
2. Chief accountant (head of the accounting unit): Record the payment in the books (SP-17). Boundary: Paper form: journal entry voucher; eFPS for taxes withheld. Control: Chief accountant, a person checks. Writes in: Agency own systems. Records: Report of Checks Issued (RCI), App.35, and Report of ADA Issued (RADAI), App.13; Disbursement Voucher (DV), App.32; List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42; Journal Entry Voucher (JEV), App.36 [Agency own systems]; Tax return (including returns of taxes withheld); Tax Remittance Advice (TRA).
3. Head of the budget unit: Post the payment in the ORS and the registry (SP-18). Boundary: Paper ORS, part C; registry of disbursements. Control: Head of the budget unit, a person checks. Writes in: Agency own systems. Records: Report of Checks Issued (RCI), App.35, and Report of ADA Issued (RADAI), App.13; Journal Entry Voucher (JEV), App.36; Obligation Request and Status (ORS), App.11 [Agency own systems]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [Agency own systems].
4. COA audit team: Audit the paid transaction (SP-19). Boundary: Paid vouchers and their documents, on paper. Control: COA auditor, a person checks. Records: Report of Checks Issued (RCI), App.35, and Report of ADA Issued (RADAI), App.13; Disbursement Voucher (DV), App.32; Journal Entry Voucher (JEV), App.36; List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42; Audit Observation Memorandum [COA audit team]; Notice of Suspension [COA audit team]; Notice of Disallowance [COA audit team]; Notice of Charge [COA audit team].

Basic course in cohort E (diagrams: robustness/UC-SP-6_E, sequence/UC-SP-6_E):

1. Cashier or disbursing officer: Receive the validated copy and prepare the daily report (SP-16). Boundary: Paper forms: validated LDDAP-ADA, official receipt of the payee, report of ADA issued (RADAI). Control: Cashier, a person checks. Writes in: Agency own systems. Records: List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42; Report of Checks Issued (RCI), App.35, and Report of ADA Issued (RADAI), App.13; Disbursement Voucher (DV), App.32.
2. Chief accountant (head of the accounting unit): Record the payment in the books (SP-17). Boundary: eNGAS: journal entry; eFPS for taxes withheld. Control: Chief accountant, a person checks. Writes in: eNGAS. Records: Report of Checks Issued (RCI), App.35, and Report of ADA Issued (RADAI), App.13; Disbursement Voucher (DV), App.32; List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42; Journal Entry Voucher (JEV), App.36 [eNGAS]; Tax return (including returns of taxes withheld); Tax Remittance Advice (TRA).
3. Head of the budget unit: Post the payment in the ORS and the registry (SP-18). Boundary: eBudget of COA. Control: Head of the budget unit, a person checks. Writes in: eBudget (COA). Records: Report of Checks Issued (RCI), App.35, and Report of ADA Issued (RADAI), App.13; Journal Entry Voucher (JEV), App.36; Obligation Request and Status (ORS), App.11 [eBudget (COA)]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [eBudget (COA)].
4. COA audit team: Audit the paid transaction (SP-19). Boundary: Paid vouchers and their documents, on paper. Control: COA auditor, a person checks. Records: Report of Checks Issued (RCI), App.35, and Report of ADA Issued (RADAI), App.13; Disbursement Voucher (DV), App.32; Journal Entry Voucher (JEV), App.36; List of Due and Demandable Accounts Payable with Advice to Debit Account (LDDAP-ADA), App.42; Audit Observation Memorandum [COA audit team]; Notice of Suspension [COA audit team]; Notice of Disallowance [COA audit team]; Notice of Charge [COA audit team].

Alternate courses:

- Taxes withheld are remitted by the 10th day of the next month through eFPS [GAM-V1 Ch.6 ss.60-62]
- The auditor may issue an observation or a notice of suspension, disallowance or charge [COA2009-006]

### UC-SP-7 Reconcile with the bank

Chain: CH-SPEND (Spending: from an allotment to a settled payment and its records). Primary actor: Chief accountant (head of the accounting unit).

Goal: Books, registries and bank agree for the period.

Basic course in cohort P (diagrams: robustness/UC-SP-7_P, sequence/UC-SP-7_P):

1. Servicing bank: Send the monthly bank statement (SP-20). Boundary: Paper bank statement with paid checks and memoranda. Control: Servicing bank, the bank checks. Records: Monthly bank statement with paid checks and debit and credit memoranda.
2. Chief accountant (head of the accounting unit): Reconcile books, registries and bank for the month (SP-21). Boundary: Bank reconciliation statement (paper or spreadsheet). Control: Chief accountant compares books, registries and statement, a person checks. Writes in: Agency own systems. Records: Monthly bank statement with paid checks and debit and credit memoranda; Bank Reconciliation Statement, App.80 for MDS accounts and App.81 for accounts in depository banks [Agency own systems]; Journal Entry Voucher (JEV), App.36 [Agency own systems]; RANCA, Registry of Allotments and Notice of Cash Allocation, App.30 [Agency own systems]; Checks and ADA Disbursements Record, App.34 [Agency own systems].

Basic course in cohort E (diagrams: robustness/UC-SP-7_E, sequence/UC-SP-7_E):

1. Servicing bank: Send the monthly bank statement (SP-20). Boundary: Paper bank statement with paid checks and memoranda. Control: Servicing bank, the bank checks. Records: Monthly bank statement with paid checks and debit and credit memoranda.
2. Chief accountant (head of the accounting unit): Reconcile books, registries and bank for the month (SP-21). Boundary: Bank reconciliation statement; books in eNGAS. Control: Chief accountant, a person checks. Writes in: Agency own systems. Records: Monthly bank statement with paid checks and debit and credit memoranda; Bank Reconciliation Statement, App.80 for MDS accounts and App.81 for accounts in depository banks [Agency own systems]; Journal Entry Voucher (JEV), App.36 [eNGAS]; RANCA, Registry of Allotments and Notice of Cash Allocation, App.30 [Agency own systems]; Checks and ADA Disbursements Record, App.34 [Agency own systems].

Basic course in cohort B (diagrams: robustness/UC-SP-7_B, sequence/UC-SP-7_B):

1. Chief accountant (head of the accounting unit): Reconcile each day from electronic statements (SP-21B). Boundary: BTMS: bank reconciliation from electronic bank statements. Control: BTMS, software checks. Writes in: BTMS: 2 Payments. Records: Electronic bank statement; Bank Reconciliation Statement, App.80 for MDS accounts and App.81 for accounts in depository banks [BTMS: 2 Payments]; Journal Entry Voucher (JEV), App.36 [BTMS: 5 Accounting and reporting]; RANCA, Registry of Allotments and Notice of Cash Allocation, App.30 [BTMS].

Alternate courses:

- Reconciling items are listed in the bank reconciliation statement [GAM-V1 Ch.21 s.4]
- In cohort B the reconciliation is daily from electronic statements (described, not verified) [BTMS-SITE]

### UC-RL Release an allotment

Chain: CH-RELEASE (Release of allotments). Primary actor: DBM (bureaus and approving officials).

Goal: The allotment is available to the agency, and its release document can be checked by any person.

Basic course in cohort P, E, B (diagrams: robustness/UC-RL_PEB, sequence/UC-RL_PEB):

1. Agency as a whole (central office): Submit the budget execution documents in URS (RL-01). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Budget Execution Documents: BED 1 Financial Plan, BED 2 Physical Plan, BED 3 Monthly Disbursement Program; Release guidelines (National Budget Circular).
2. DBM (bureaus and approving officials): Pass the documents to DBM (RL-02). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: URS. Records: Budget Execution Documents: BED 1 Financial Plan, BED 2 Physical Plan, BED 3 Monthly Disbursement Program.
3. DBM (bureaus and approving officials): Release by the GAA as allotment order (RL-03A). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Budget Execution Documents: BED 1 Financial Plan, BED 2 Physical Plan, BED 3 Monthly Disbursement Program; General Appropriations Act (GAA) [e-Budget (DBM)]; Special Allotment Release Order (SARO) [Agency own systems]; GAA as allotment order (GAAAO) [Agency own systems]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [Agency own systems].
4. Agency as a whole (central office): Submit a Special Budget Request (RL-03B). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Budget Execution Documents: BED 1 Financial Plan, BED 2 Physical Plan, BED 3 Monthly Disbursement Program; Special Budget Request (SBR) [DBM].
5. Office of the President: Obtain the approval of the Office of the President (RL-04A). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Special Budget Request (SBR) [DBM].
6. DBM (bureaus and approving officials): No approval of the President needed (RL-04B). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Special Budget Request (SBR) [DBM].
7. DBM (bureaus and approving officials): Evaluate and approve the SARO or GARO (RL-05). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Special Budget Request (SBR); General Appropriations Act (GAA) [e-Budget (DBM)]; Special Allotment Release Order (SARO); General Allotment Release Order (GARO).
8. DBM (bureaus and approving officials): Release the document in ADRS (RL-06). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: ADRS. Records: Special Allotment Release Order (SARO); General Allotment Release Order (GARO); Verification record of an issued release document.
9. Head of the budget unit: Download and record the allotment (RL-07). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Special Allotment Release Order (SARO); General Allotment Release Order (GARO); GAA as allotment order (GAAAO) [Agency own systems]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [Agency own systems].
10. DBM (bureaus and approving officials): Store the fingerprint of the document (RL-08). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: Document verification (blockchain). Records: Verification record of an issued release document.

Alternate courses:

- Items without pre-conditions: the GAA itself is the allotment order [NBC599 s.3.7]
- Items that need clearance: Special Budget Request, and for some items approval of the Office of the President [NBC599]

### UC-PR Procure up to the award

Chain: CH-PROC (Procurement in PhilGEPS up to the award). Primary actor: BAC, its Secretariat and technical working group.

Goal: An award is made after a public notice, and the plan and report are with the GPPB.

Basic course in cohort P, E (diagrams: robustness/UC-PR_PE, sequence/UC-PR_PE):

1. BAC, its Secretariat and technical working group: Submit the procurement plan and monitoring report (PR-01). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Annual Procurement Plan (APP), indicative and final; Procurement Monitoring Report; Purchase Request, App.60 [Agency own systems].
2. BAC, its Secretariat and technical working group: Post the invitation to bid (PR-02). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Invitation to bid and bidding documents; Purchase Request, App.60 [Agency own systems]; Annual Procurement Plan (APP), indicative and final [Agency own systems].
3. Procurement Service of DBM: Show the opportunity and publish open data (PR-03). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: PhilGEPS (modernized). Records: Invitation to bid and bidding documents; Notice of award.
4. Supplier or contractor: Submit and open the bids (PR-04). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Invitation to bid and bidding documents; Bid [PhilGEPS (modernized): Electronic bidding].
5. Head of agency or authorized official: Evaluate, recommend and award (PR-05). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Bid [PhilGEPS (modernized): Electronic bidding]; Purchase Request, App.60 [Agency own systems]; Annual Procurement Plan (APP), indicative and final [Agency own systems]; Notice of award [PhilGEPS (modernized)]; Resolution of the BAC recommending award [PhilGEPS (modernized)].

Basic course in cohort B (diagrams: robustness/UC-PR_B, sequence/UC-PR_B):

1. BAC, its Secretariat and technical working group: Submit the procurement plan and monitoring report (PR-01). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Annual Procurement Plan (APP), indicative and final; Procurement Monitoring Report; Purchase Request, App.60 [BTMS: 1 Commitment and obligations].
2. BAC, its Secretariat and technical working group: Post the invitation to bid (PR-02). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Invitation to bid and bidding documents; Purchase Request, App.60 [BTMS: 1 Commitment and obligations]; Annual Procurement Plan (APP), indicative and final [BTMS: 1 Commitment and obligations].
3. Procurement Service of DBM: Show the opportunity and publish open data (PR-03). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: PhilGEPS (modernized). Records: Invitation to bid and bidding documents; Notice of award.
4. Supplier or contractor: Submit and open the bids (PR-04). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Invitation to bid and bidding documents; Bid [PhilGEPS (modernized): Electronic bidding].
5. Head of agency or authorized official: Evaluate, recommend and award (PR-05). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Bid [PhilGEPS (modernized): Electronic bidding]; Purchase Request, App.60 [BTMS: 1 Commitment and obligations]; Annual Procurement Plan (APP), indicative and final [BTMS: 1 Commitment and obligations]; Notice of award [PhilGEPS (modernized)]; Resolution of the BAC recommending award [PhilGEPS (modernized)].
6. Procurement Service of DBM: Pass procurement data to BTMS (planned) (PR-06). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: PhilGEPS (modernized). Records: Notice of award; Procurement data for BTMS (content not stated).

Alternate courses:

- Bids through the electronic bidding facility or on paper [GPPB2025-09]
- Procurement data to BTMS is planned (cohort B) [CL2025-8]

### UC-CO Collect a fee and deposit it

Chain: CH-COLLECT (Collections of an agency to the Treasury). Primary actor: Collecting officer.

Goal: The fee is in the books of the agency and its cash reaches the Treasury Single Account.

Basic course in cohort P, E (diagrams: robustness/UC-CO_PE, sequence/UC-CO_PE):

1. Collecting officer: Pay the fee (CO-01). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Order of Payment, App.28, and official receipt; Fees paid to an agency (money).
2. Collecting officer: Issue the official receipt (CO-02). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Fees paid to an agency (money); Order of Payment, App.28, and official receipt.
3. Collecting officer: Deposit the collections in full (CO-03). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Order of Payment, App.28, and official receipt; Deposit of agency collections (money).
4. Collecting officer: Report collections and deposits for the day (CO-04). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Order of Payment, App.28, and official receipt [Agency own systems]; Report of Collections and Deposits, App.26.
5. Authorized government depository bank: Credit the account and report (CO-05). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Deposit of agency collections (money); Daily and monthly collection reports of a depository bank; Consolidated report of daily collections, with the credit memo or abstract of deposits.
6. Chief accountant (head of the accounting unit): Record the collections (CO-06). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Report of Collections and Deposits, App.26; Consolidated report of daily collections, with the credit memo or abstract of deposits; Journal Entry Voucher (JEV), App.36 [Agency own systems].
7. Authorized government depository bank: Transfer the balances to the TSA (CO-07). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Transfer of the balances of depository banks to the Treasury Single Account (money).
8. Bureau of the Treasury: Consolidate the collection reports (CO-08). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: NGCDS. Records: Daily and monthly collection reports of a depository bank.
9. Bureau of the Treasury: Issue the certificate of deposited collections (CO-09). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Daily and monthly collection reports of a depository bank; Certificate of deposited national collections.
10. Agency as a whole (central office): Report revenue and other receipts (FAR 5) (CO-10). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Journal Entry Voucher (JEV), App.36 [Agency own systems]; FAR 5, Quarterly Report of Revenue and Other Receipts.

Basic course in cohort B (diagrams: robustness/UC-CO_B, sequence/UC-CO_B):

1. Collecting officer: Pay the fee (CO-01). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Order of Payment, App.28, and official receipt; Fees paid to an agency (money).
2. Collecting officer: Issue the official receipt (CO-02). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Fees paid to an agency (money); Order of Payment, App.28, and official receipt.
3. Collecting officer: Deposit the collections in full (CO-03). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Order of Payment, App.28, and official receipt; Deposit of agency collections (money).
4. Collecting officer: Report collections and deposits for the day (CO-04). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Order of Payment, App.28, and official receipt [BTMS: 3 Receipts]; Report of Collections and Deposits, App.26.
5. Authorized government depository bank: Credit the account and report (CO-05). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Deposit of agency collections (money); Daily and monthly collection reports of a depository bank; Consolidated report of daily collections, with the credit memo or abstract of deposits.
6. Chief accountant (head of the accounting unit): Record the collections (CO-06). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Report of Collections and Deposits, App.26; Consolidated report of daily collections, with the credit memo or abstract of deposits; Journal Entry Voucher (JEV), App.36 [BTMS: 3 Receipts].
7. Authorized government depository bank: Transfer the balances to the TSA (CO-07). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Transfer of the balances of depository banks to the Treasury Single Account (money).
8. Bureau of the Treasury: Consolidate the collection reports (CO-08). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: NGCDS. Records: Daily and monthly collection reports of a depository bank.
9. Bureau of the Treasury: Issue the certificate of deposited collections (CO-09). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Daily and monthly collection reports of a depository bank; Certificate of deposited national collections.

### UC-TX Collect taxes and duties

Chain: CH-TAX (Tax and customs collections). Primary actor: Taxpayer or importer.

Goal: The return is posted, the goods are released, and the collections reach the Treasury Single Account.

Basic course in cohort P, E, B (diagrams: robustness/UC-TX_PEB, sequence/UC-TX_PEB):

1. Taxpayer or importer: File the return (TX-01). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Tax return (including returns of taxes withheld).
2. Taxpayer or importer: Pay the tax (TX-02). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Tax or duty payment (money).
3. BIR office or approving official: Pass the return to the internal system (TX-03). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: eFPS and eBIRForms. Records: Tax return (including returns of taxes withheld).
4. Authorized agent bank or payment gateway: Confirm and report the payment (TX-04). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Tax or duty payment (money); Report of tax payments received by a bank.
5. BIR office or approving official: Post the payment to the taxpayer account (TX-05). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: BIR internal tax system. Records: Tax return (including returns of taxes withheld); Report of tax payments received by a bank.
6. Authorized agent bank or payment gateway: Remit the collections to the TSA (TX-06). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Remittance of tax and customs collections to the Treasury Single Account (money).
7. BSP: Credit the TSA (TX-07). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: Treasury Single Account. Records: Remittance of tax and customs collections to the Treasury Single Account (money).
8. Taxpayer or importer: Declare the goods (TX-11). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Goods declaration (customs).
9. BOC: Assess duties and taxes (TX-12). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: E2M customs system. Records: Goods declaration (customs).
10. Taxpayer or importer: Pay the assessed amount (TX-13). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Tax or duty payment (money).
11. Authorized agent bank or payment gateway: Send the abstract of collection through PAS (TX-14). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Tax or duty payment (money); Abstract of customs collections.
12. BOC: Confirm the payment and release the goods (TX-15). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: E2M customs system. Records: Abstract of customs collections.

### UC-DB Borrow through government securities

Chain: CH-DEBT (Borrowing through government securities). Primary actor: Bureau of the Treasury.

Goal: The proceeds are in the Treasury Single Account and the debt is recorded and serviced.

Basic course in cohort P, E, B (diagrams: robustness/UC-DB_PEB, sequence/UC-DB_PEB):

1. Dealer or lender: Bid in the auction (DB-01). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Bid in an auction of government securities.
2. Bureau of the Treasury: Award and send the settlement instruction (DB-02). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: NRoSS. Records: Bid in an auction of government securities; Settlement instruction for securities.
3. BSP: Settle securities against payment (DB-03). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: PhilPaSSplus. Records: Settlement instruction for securities; Proceeds of securities and loans (money).
4. BSP: Credit the proceeds to the TSA (DB-04). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: Treasury Single Account. Records: Proceeds of securities and loans (money).
5. Bureau of the Treasury: Record the new debt (DB-05). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: BTr debt recording system. Records: Record of new debt.
6. Bureau of the Treasury: Pay interest and principal (DB-06). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Interest and principal (money).

### UC-RP Report on budget execution

Chain: CH-REPORT (Reporting). Primary actor: Agency as a whole (central office).

Goal: DBM, COA, BTr and the public receive the reports.

Basic course in cohort P, E (diagrams: robustness/UC-RP_PE, sequence/UC-RP_PE):

1. Agency as a whole (central office): Prepare the accountability reports in URS (RP-01). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: BAR 1, Quarterly Physical Report of Operations; FAR 1, Statement of Appropriations, Allotments, Obligations, Disbursements and Balances, with 1-A (by object), 1-B (list of allotments and sub-allotments), 1-C (inter-agency fund transfers); FAR 2 and 2-A; FAR 3, Aging of Due and Demandable Obligations; FAR 4, Monthly Report of Disbursements; FAR 5, Quarterly Report of Revenue and Other Receipts; FAR 6; Obligation Request and Status (ORS), App.11 [Agency own systems]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [Agency own systems]; Journal Entry Voucher (JEV), App.36 [Agency own systems].
2. DBM (bureaus and approving officials): Pass the reports to DBM, COA and BTr (RP-02). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: URS. Records: BAR 1, Quarterly Physical Report of Operations; FAR 1, Statement of Appropriations, Allotments, Obligations, Disbursements and Balances, with 1-A (by object), 1-B (list of allotments and sub-allotments), 1-C (inter-agency fund transfers); FAR 2 and 2-A; FAR 3, Aging of Due and Demandable Obligations; FAR 4, Monthly Report of Disbursements; FAR 5, Quarterly Report of Revenue and Other Receipts; FAR 6.
3. Chief accountant (head of the accounting unit): Submit the financial statements (RP-04). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Trial balance and the six financial statements: financial position, financial performance, changes in net assets or equity, cash flows, comparison of budget and actual amounts, and notes; Journal Entry Voucher (JEV), App.36 [Agency own systems].
4. COA: Prepare the Annual Financial Report (RP-05). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Trial balance and the six financial statements: financial position, financial performance, changes in net assets or equity, cash flows, comparison of budget and actual amounts, and notes; Annual Financial Report [Government Accountancy Sector].
5. Agency as a whole (central office): Submit information to COMPASS (RP-06). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Entry in the COMPASS portal; Obligation Request and Status (ORS), App.11 [Agency own systems]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [Agency own systems].
6. DBM (bureaus and approving officials): Publish budget and spending figures (RP-08). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: COMPASS portal. Records: Entry in the COMPASS portal.

Basic course in cohort B (diagrams: robustness/UC-RP_B, sequence/UC-RP_B):

1. DBM (bureaus and approving officials): Produce the reports from BTMS records (RP-03). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: BTMS: 5 Accounting and reporting. Records: FAR 1, Statement of Appropriations, Allotments, Obligations, Disbursements and Balances, with 1-A (by object), 1-B (list of allotments and sub-allotments), 1-C (inter-agency fund transfers); FAR 3, Aging of Due and Demandable Obligations; FAR 4, Monthly Report of Disbursements; FAR 5, Quarterly Report of Revenue and Other Receipts; Journal Entry Voucher (JEV), App.36 [BTMS: 5 Accounting and reporting]; Obligation Request and Status (ORS), App.11 [BTMS]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [BTMS].
2. Chief accountant (head of the accounting unit): Submit the financial statements (RP-04). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Trial balance and the six financial statements: financial position, financial performance, changes in net assets or equity, cash flows, comparison of budget and actual amounts, and notes; Journal Entry Voucher (JEV), App.36 [BTMS: 5 Accounting and reporting].
3. COA: Prepare the Annual Financial Report (RP-05). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Trial balance and the six financial statements: financial position, financial performance, changes in net assets or equity, cash flows, comparison of budget and actual amounts, and notes; Annual Financial Report [Government Accountancy Sector].
4. Agency as a whole (central office): Submit information to COMPASS (RP-06). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Entry in the COMPASS portal; Obligation Request and Status (ORS), App.11 [BTMS]; RAOD, Registries of Allotments, Obligations and Disbursements, App.9A to 9D [BTMS].
5. DBM (bureaus and approving officials): Pass BTMS data to COMPASS (described) (RP-07). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: BTMS. Records: Entry in the COMPASS portal; Journal Entry Voucher (JEV), App.36 [BTMS: 5 Accounting and reporting].
6. DBM (bureaus and approving officials): Publish budget and spending figures (RP-08). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: COMPASS portal. Records: Entry in the COMPASS portal.

Alternate courses:

- Agencies on BTMS: reports produced from BTMS records [CL2025-8]
- Until migration: reports through URS or other electronic means [GAA2026-GP]

### UC-PL From the investment program to the enacted budget

Chain: CH-PLAN (From the investment program to the enacted budget in the systems). Primary actor: Planning and budget officer of the agency.

Goal: The enacted budget is in the systems of DBM and can be released.

Basic course in cohort P, E, B (diagrams: robustness/UC-PL_PEB, sequence/UC-PL_PEB):

1. Planning and budget officer of the agency: Encode and endorse programs and projects in PIPOL (PL-01). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Entry of a program or project in PIPOL.
2. DEPDev PIP and TRIP secretariats: Validate the entries against the PIP criteria (PL-02). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Entry of a program or project in PIPOL; Public Investment Program (PIP) 2023-2028 [PIPOL]; Three-Year Rolling Infrastructure Program (TRIP) [PIPOL].
3. Planning and budget officer of the agency: Enter the budget proposal in OSBPS (PL-03). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Budget Call (National Budget Memorandum); Budget Preparation (BP) forms; Public Investment Program (PIP) 2023-2028 [PIPOL]; Three-Year Rolling Infrastructure Program (TRIP) [PIPOL].
4. Personnel officer: Update the positions in GMIS (PL-04). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Monthly update of positions in GMIS (PSIPOP).
5. DBM (bureaus and approving officials): Build the proposed budget (PL-05). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: BPMS. Records: Budget Preparation (BP) forms; Monthly update of positions in GMIS (PSIPOP).
6. Congress: Enact the budget (PL-06). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Records: Budget Preparation (BP) forms; Monthly update of positions in GMIS (PSIPOP); National Expenditure Program (NEP) [BPMS].
7. DBM (bureaus and approving officials): Load the enacted budget in the e-Budget of DBM (PL-07). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: e-Budget (DBM). Records: National Expenditure Program (NEP) [BPMS]; General Appropriations Act (GAA).
8. DBM (bureaus and approving officials): Make the appropriation available for release (PL-08). Boundary: System or office where the act takes place. Control: Not stated in detail, the check is not stated. Writes in: e-Budget (DBM). Records: General Appropriations Act (GAA).

Alternate courses:

- Projects that need appraisal go to the ICC and the ED Council (diagram 01b, optional block) [AO37]

## Business use cases from the sequence diagrams of the atlas

### BUC-01b Investment programming: how a project enters the PIP and TRIP and reaches the budget

Source: atlas diagram 01b (01b_investment_programming_sequence.mmd). Actors: DEPDev PIP and TRIP secretariats, Agency as a whole (central office), Regional office or operating unit, Regional Development Council, ICC, ED Council, DBM (bureaus and approving officials).

Basic course:

- 1. PIP and TRIP secretariats to National agency: Joint call to update the PIP and formulate the TRIP, with guidelines and calendar
- 2. Operating units to Regional Development Councils: Regional priority programs and projects
- 3. Regional Development Councils to Operating units: Endorsement, or recommendations
- 4. National agency to PIPOL: Reconfirm ongoing programs and projects. Encode new or updated ones: cost per year, physical and financial progress
- 5. National agency to PIPOL: Head of agency endorses the submission (example window: 8 November to 6 December 2024)
- 6. PIPOL to PIP and TRIP secretariats: Only submissions marked "as endorsed" are processed
- 7. PIP and TRIP secretariats: Check each entry against the PIP criteria and the scope of the TRIP
- 12. PIP and TRIP secretariats to DBM: PIP and TRIP as input to budget preparation
- 13. DBM to National agency: Budget Call. A Tier 2 proposal must be implementation-ready and must have the required endorsements and approvals
- 14. National agency to DBM: Tier 2 proposals in OSBPS (a different system from PIPOL)
- 15. National agency to PIPOL: After the budget is known, update yearly costs to match the GAA and the National Expenditure Program

Alternate courses:

- Only when: Project needs ICC review: 8. National agency to ICC: Project proposal with feasibility study and financing plan 9. ICC: Technical, economic and financial appraisal 10. ICC to ED Council: Recommendation 11. ED Council to National agency: Approval or confirmation

### BUC-03a Budget preparation: from the fiscal program to the President's budget (example: FY 2027 budget, prepared in 2026)

Source: atlas diagram 03a (03a_budget_preparation_sequence.mmd). Actors: DBCC, DBM (bureaus and approving officials), Agency as a whole (central office), Regional office or operating unit, Regional Development Council, Civil society organization, President and Cabinet, Congress.

Basic course:

- 1. DBCC to DBM: Fiscal program: revenue, spending ceiling, deficit, borrowing
- 2. DBM to National agency: Budget Call (National Budget Memorandum No. 156): policy, budget levels, forms, calendar. Budget Forum 28-29 January 2026
- 3. DBM to National agency: Forward Estimates for FY 2027-2029, formulated by DBM with the agency (basis of Tier 1)
- 4. National agency to Operating units: Internal call for proposals
- (at the same time:)
-   (Regional consultation)
- 5. Operating units to Regional Development Councils: Regional proposals for priority programs and projects
- 6. Regional Development Councils to National agency: Inputs and recommendations (BP Form C). DEPDev regional offices send consolidated RDC resolutions to DBM
-   (Civil society consultation)
- 7. National agency to Civil society: Consultation on proposed programs
- 8. Civil society to National agency: Inputs (reported in BP Form D)
- 9. National agency to OSBPS: TIER 1: cost of ongoing programs and commitments at the same scope and quality (BP Forms 201-A to 201-D, 204, 205, 100 series, A and B). Submission period 6 March to 28 April 2026
- 10. National agency to OSBPS: TIER 2: new or expanded programs and projects (BP Form 202, and 203 for foreign-assisted projects), implementation-ready and endorsed
- 11. National agency to DBM: Two printed copies. The electronic copy prevails
- 12. OSBPS to DBM: Encoded proposals
- 13. DBM to National agency: Technical budget hearings: the agency justifies its proposal
- 14. DBM: Evaluation and executive review. Tier 2 proposals compete for the fiscal space (spending program minus total Tier 1)
- 15. DBM to DBCC: Proposed budget levels
- 16. DBCC to Cabinet: Recommended budget
- 17. Cabinet to DBM: Approval by the President and the Cabinet
- 18. DBM: Prepare the budget documents: National Expenditure Program (NEP), Budget of Expenditures and Sources of Financing (BESF), President's Budget Message, staffing summary
- 19. Cabinet to Congress: Submit the budget within 30 days from the opening of the regular session (for FY 2027: by 26 August 2026. Press reports: submitted on 11 August 2026)

### BUC-04a Budget legislation: from the President's budget to the General Appropriations Act (GAA)

Source: atlas diagram 04a (04a_legislation_sequence.mmd). Actors: President, House plenary, House Committee on Appropriations, DBCC, Agency as a whole (central office), Senate Committee on Finance, Senate plenary, Bicameral Conference Committee, DBM (bureaus and approving officials).

Basic course:

- 1. President to House plenary: President's budget: NEP, BESF, Budget Message, within 30 days from the opening of the regular session
- 2. House plenary to House Appropriations: The NEP is filed as the General Appropriations Bill (GAB) and referred to the committee
- 3. DBCC to House Appropriations: Briefing on the economy and the fiscal program
- (at the same time:)
-   (House committee stage)
- 4. House Appropriations to National agency: Hearings, agency by agency: plans, past performance
- 5. National agency to House Appropriations: Answers and documents
-   (Senate committee stage, at the same time)
- 6. Senate Finance to National agency: Hearings, agency by agency
- 7. National agency to Senate Finance: Answers and documents
- 8. House Appropriations to House plenary: Committee report on the GAB
- 9. House plenary: Plenary debates and amendments. Approval on second and third reading
- 10. House plenary to Senate plenary: GAB as approved by the House
- 11. Senate Finance to Senate plenary: Committee report with Senate amendments
- 12. Senate plenary: Plenary debates and amendments. Approval on second and third reading
- 13. House plenary to Bicameral committee: House conferees and House version
- 14. Senate plenary to Bicameral committee: Senate conferees and Senate version
- 15. Bicameral committee: Reconcile the two versions
- 16. Bicameral committee to House plenary: Conference report
- 17. Bicameral committee to Senate plenary: Conference report
- 18. House plenary to President: Both chambers ratify. The enrolled bill goes to the President
- 19. President: Review. May veto particular items. The items not vetoed become law
- 20. President to DBM: Signed General Appropriations Act (GAA)

Alternate courses:

- Only when: Congress disagrees with a veto: 21. House plenary to President: Override by two thirds of each chamber

### BUC-05a Release of funds: two separate authorities, allotment (to commit) and cash authority (to pay). Example: FY 2026

Source: atlas diagram 05a (05a_release_sequence.mmd). Actors: DBM (bureaus and approving officials), Agency as a whole (central office), Regional office or operating unit, Office of the President, Bureau of the Treasury, Servicing bank.

Basic course:

- 1. DBM to National agency: Release guidelines for the year (National Budget Circular)
- 2. National agency to URS: Budget execution documents: BED 1 Financial Plan, BED 2 Physical Plan, BED 3 Monthly Disbursement Program
- 3. URS to DBM: Documents for evaluation
- (choice: Item without pre-conditions (Schedule I). Example: salaries of filled positions)
- 4. DBM to Operating units: No separate document. The GAA itself is the allotment order (GAAAO). Items appropriated to a regional office or operating unit go directly to it
- 11. National agency to Operating units: Sub-allotment to lower units, where the central office holds the allotment
- 12. BTr to DBM: Cash position of the national government
- 13. DBM to Servicing banks: Notice of Cash Allocation (NCA). First NCA covers the first quarter. Later NCAs follow the Monthly Disbursement Program, subject to spending performance and the fiscal position
- 14. Servicing banks: Credit the limit to the MDS sub-account of the unit: regular, special accounts, trust, or foreign-assisted projects
- 15. DBM to ADRS: Advice of NCA Issued
- 16. ADRS to Operating units: Agency downloads the advice
- 19. National agency to Operating units: Notice of Transfer of Allocation, where the central office shares its own NCA with a lower unit

Alternate courses:

- Only when: Item for which the guidelines require it: 6. DBM to Office of the President: Request for approval 7. Office of the President to DBM: Approval
- Instead, when: Item that needs clearance (Schedule II). Examples: lump sums, new items, special purpose funds: 5. National agency to DBM: Special Budget Request with details: project profile, location, cost, certifications 8. DBM: Evaluate: conditions of the GAA, readiness, past spending capacity of the agency 9. DBM to ADRS: Approved SARO (Special Allotment Release Order) or GARO (General Allotment Release Order) 10. ADRS to National agency: Authorized users of the agency download the document
- Only when: Cash need above the program: 17. National agency to DBM: Request for additional NCA 18. DBM to Servicing banks: Additional NCA

### BUC-06b Competitive bidding under the New Government Procurement Act (RA 12009): who does what, with the time limits

Source: atlas diagram 06b (06b_competitive_bidding_sequence.mmd). Actors: Head of the requesting office, BAC, its Secretariat and technical working group, Head of the budget unit, Supplier or contractor, Observer in procurement, Head of agency or authorized official, COA.

Basic course:

- 1. Requesting office to BAC and procurement unit: Purchase request, specifications, bidding documents for an item in the Annual Procurement Plan
- 2. BAC and procurement unit to Budget unit: Are appropriations available for this procurement?
- 3. Budget unit to BAC and procurement unit: Confirmation: the item is in the budget law, or in the proposed budget for early procurement
- 4. BAC and procurement unit: Pre-procurement conference: the procurement follows the plan, appropriations are available, the award criterion is chosen
- 5. BAC and procurement unit to PhilGEPS (modernized): Post the invitation to bid and the bidding documents, with the budget for the contract and the source of funding. Also on the website of the entity, and 7 days at its premises
- 6. PhilGEPS (modernized) to Suppliers and payees: Notice visible to registered suppliers
- 7. BAC and procurement unit to Suppliers and payees: Pre-bid conference, at least 12 days before the deadline for bids (required from a budget of PHP 3 million)
- 8. Suppliers and payees to BAC and procurement unit: Bids in two sealed envelopes: technical (with eligibility documents and bid security) and financial. Deadline: at most 45 days (goods), 50 or 65 (works), 75 (consulting) after posting
- 9. BAC and procurement unit to Observers: Invitation to observe each stage: at least two observers, in addition to the representative of COA
- 10. BAC and procurement unit: Opening of bids immediately after the deadline. Each envelope passes or fails. A bid above the approved budget for the contract is rejected
- 11. BAC and procurement unit: Bid evaluation: 7 days for the lowest calculated bid, 14 days when quality is rated with price, 21 days for consulting. Rank by the award criterion
- (repeated: Until one bidder passes, starting from the first in rank)
- 12. BAC and procurement unit to Suppliers and payees: Post-qualification within 12 days: verify the legal, technical and financial documents, with the latest tax returns
- 13. BAC and procurement unit to Head of agency: Recommendation of award, with the document that authorizes the entity to incur the obligation
- 14. Head of agency to Suppliers and payees: Approval within 10 days, then the notice of award immediately
- 15. Head of agency to PhilGEPS (modernized): Award published
- 16. Suppliers and payees to Head of agency: Performance security, before signing: 5 percent (goods, consulting) or 10 percent (works) of the contract price, 30 percent as a surety bond
- 17. Head of agency to Suppliers and payees: Contract signed within 10 days from receipt of the notice of award
- 18. Head of agency to Suppliers and payees: Notice to proceed within 3 days from approval of the contract
- 19. Observers to Head of agency: Observation report (also to PhilGEPS, and copies to the GPPB and the Ombudsman)
- 20. Observers to COA: Observation report

Alternate courses:

- Only when: A losing bidder objects: 21. Suppliers and payees to BAC and procurement unit: Request for reconsideration within 3 days. The BAC decides within 7 days 22. Suppliers and payees to Head of agency: Protest within 7 days, filed electronically, with a fee that is not returned. Decision within 7 days. It is final for smaller contracts. For the others: review by the Regional Trial Court

### BUC-07a From obligation to payment: who certifies what, and which record each step writes (goods bought by a national agency, paid by payment order)

Source: atlas diagram 07a (07a_obligation_to_payment_sequence.mmd). Actors: Head of the requesting office, Head of the budget unit, Chief accountant (head of the accounting unit), Head of agency or authorized official, Supplier or contractor, Inspection officer and property custodian, Cashier or disbursing officer, Servicing bank, Bureau of the Treasury, BIR office or approving official, COA audit team.

Basic course:

- 1. Requesting office to Budget unit: Obligation Request and Status (ORS) with the contract or purchase order. Box A: charges are necessary, lawful and under my direct supervision, and the supporting documents are valid, proper and legal
- 2. Budget unit: Check the allotment in the registry. Assign the ORS number. Enter the obligation in the registry. Box B: allotment available and obligated. No journal entry
- 3. Accounting unit to Head of agency: Purchase order or contract with the certificate of the chief accountant: "Funds Available", and the number, date and amount of the ORS
- 4. Head of agency to Suppliers and payees: Signed purchase order or contract
- 5. Suppliers and payees to Property and inspection: Delivery, with delivery receipt and invoice
- 6. Property and inspection: Inspection and acceptance report with the numbers of the purchase order and of the invoice. Inspection officer: inspected, verified and found in order as to quantity and specifications. Property custodian: accepted, complete or partial
- 7. Property and inspection to Accounting unit: Copy of the acceptance report, with the purchase order and the delivery receipt
- 8. Accounting unit to Budget unit: Journal entry voucher (JEV): debit the asset or expense, credit Accounts Payable. The budget unit enters the payable in part C of the ORS
- 9. Requesting office to Accounting unit: DV with the original acceptance report, delivery receipt, purchase order and a copy of the ORS. Box A: expenses necessary, lawful and incurred under my direct supervision
- 10. Accounting unit: Check the documents against a list. Assign the DV number. Look into the index of payments: was this claim paid before? Compare the DV with the ORS. Box B: the accounting entry
- 11. Accounting unit: Head of accounting looks into the registry of the NCA. If the balance is enough: enter the amount as used, and sign Box C: cash available, supporting documents complete, amount claimed proper. If not: keep the DV until cash is available
- 12. Accounting unit to Head of agency: DV for approval
- 13. Head of agency to Accounting unit: Box D: approved for payment
- 14. Accounting unit to Head of agency: LDDAP-ADA in five copies for the approved DVs. The chief accountant signs "Certified Correct"
- 15. Head of agency to Cash unit: Signs "Approved"
- 16. Cash unit: Enter it in the record of checks and payment orders, with the new balance of the NCA. The cashier signs the advice to debit the account
- 17. Cash unit to Head of agency: LDDAP-ADA for the second signature
- 18. Head of agency to Cash unit: Countersigns the advice to debit the account
- 19. Cash unit: Stamp "PAID" on the payment order, the DVs and the documents. Prepare the summary list (SLIIE) in four copies. The cashier certifies it, the head of agency approves it
- 20. Cash unit to Servicing banks: Summary list and LDDAP-ADA (paper copies, or through the electronic facility of the bank)
- 21. Servicing banks: Check the payment order and the NCA balance. Debit the MDS sub-account of the agency
- 22. Servicing banks to Suppliers and payees: Credit the account of the payee with the net amount, not earlier than 24 hours and not later than 48 hours after receipt
- 23. Servicing banks to BTr: One copy of the summary list and of the LDDAP-ADA on the same day
- 24. Treasury Single Account to Servicing banks: Replenishment from the Treasury Single Account
- 25. Servicing banks to Cash unit: Validated copy of the LDDAP-ADA. Items that could not be credited are marked as not paid
- 26. Suppliers and payees to Cash unit: Official receipt, or other evidence that the payment was received
- 27. Cash unit to Accounting unit: Daily report of payment orders issued (RADAI) in four copies, with the DVs and the validated LDDAP-ADA
- 28. Accounting unit: JEV for the payment: debit Accounts Payable, credit Cash-MDS, Regular and Due to BIR. Enter it in the journal of payment orders
- 29. Accounting unit to Budget unit: One copy of the RADAI. The budget unit enters the payment in part C of the ORS and the disbursement in the registry
- 30. Accounting unit to BIR: Tax withheld: returns filed in the electronic system of BIR, paid by Tax Remittance Advice by the 10th day of the next month. No cash moves
- 31. Accounting unit to COA audit team: First copy of the RADAI and of the JEV, with the original DV, its documents and the validated LDDAP-ADA
- 32. COA audit team to Head of agency: Audit observations, or notices of suspension or disallowance (chapter 09)

### BUC-07d Payment and settlement: how money moves from the Treasury Single Account to the payee (Modified Disbursement System)

Source: atlas diagram 07d (07d_payment_settlement_sequence.mmd). Actors: DBM (bureaus and approving officials), Servicing bank, Chief accountant (head of the accounting unit), Cashier or disbursing officer, Supplier or contractor, Bureau of the Treasury, BSP.

Basic course:

- 1. DBM to Servicing banks: NCA: limit for the MDS sub-account of the agency
- 2. Accounting unit: Books: debit Cash-MDS, Regular, credit Subsidy from National Government. Registry of the NCA. No official receipt is issued for an NCA
- 3. Cash unit to Servicing banks: Payment order (LDDAP-ADA) in three copies and summary list (SLIIE) in two, on paper or through the electronic facility of the bank
- 4. Accounting unit: Books, on the day of the daily report: credit Cash-MDS, Regular
- 5. Servicing banks: Check the payment order and the NCA balance. Debit the MDS sub-account (the NCA balance decreases)
- (choice: Payee has an account in the same bank)
- 6. Servicing banks to Suppliers and payees: Direct credit, not earlier than 24 hours and not later than 48 hours after receipt
- 8. Servicing banks to BTr: One copy of the summary list and of the payment order on the same day: notice of the amount to be replenished
- 9. BTr to BSP: Instruction to replenish the servicing bank
- 10. Treasury Single Account to Servicing banks: Debit the Treasury account, credit the account of the bank at BSP
- 11. BTr: Books of the Treasury: debit Subsidy to NGAs, credit Cash in Bank
- 12. Servicing banks to Cash unit: Validated copy of the payment order. Items that could not be credited are marked
- 13. Accounting unit: For an item not credited: journal entry to cancel it, and a new payment order. Each month: reconcile the books with the bank statement of the sub-account

Alternate courses:

- Instead, when: Payee has an account in another bank: 7. Servicing banks to Suppliers and payees: Bank transfer. The payee bears the bank charge

### BUC-07i A works contract with an advance, progress billings and retention money (example of the Manual)

Source: atlas diagram 07i (07i_advance_progress_retention.mmd). Actors: Supplier or contractor, Cashier or disbursing officer, Head of the budget unit, Project unit and engineer, Chief accountant (head of the accounting unit).

Basic course:

- 1. Suppliers and payees to Cash unit: Performance security before the contract is signed. In the example: cash of 75,000. Books: Guaranty/Security Deposits Payable 75,000
- 2. Budget unit: Obligation for the whole contract price: 800,000 in the registry. No journal entry
- 3. Suppliers and payees to Project unit: Written request for an advance, with a letter of credit, a bank guarantee or a surety bond
- 4. Accounting unit to Suppliers and payees: Advance of 15 percent: 120,000. Books: debit Advances to Contractors 120,000, credit Cash-MDS, Regular 120,000
- 5. Suppliers and payees to Project unit: Statement of work accomplished: 400,000
- 6. Project unit to Accounting unit: The engineer checks the statement and certifies the amount to be paid
- 7. Accounting unit: Books: debit Construction in Progress 400,000. Credit Advances to Contractors 60,000 (half of the advance is recovered) and Accounts Payable 340,000
- 8. Accounting unit to Suppliers and payees: Payment of 282,200. Books: debit Accounts Payable 340,000. Credit Cash-MDS, Regular 282,200, Guaranty/Security Deposits Payable 34,000 (retention), Due to BIR 23,800 (tax withheld)
- 9. Suppliers and payees to Project unit: Statement of work accomplished: 400,000. Certificate of completion
- 10. Accounting unit: Books: debit Construction in Progress 400,000. Credit Advances to Contractors 60,000 and Accounts Payable 340,000
- 11. Suppliers and payees to Cash unit: Damages for the delay: 8,000, collected in cash. Books: Miscellaneous Income 8,000
- 12. Accounting unit to Suppliers and payees: Payment of 282,200. Retention 34,000. Tax withheld 23,800
- 13. Accounting unit: Turn-over of the building. Books: debit Buildings 800,000, credit Construction in Progress 800,000
- 14. Accounting unit to Suppliers and payees: Release of the retention money: 68,000. Books: debit Guaranty/Security Deposits Payable 68,000, credit Cash-MDS, Regular 68,000
- 15. Cash unit to Suppliers and payees: Return of the performance security: 75,000

### BUC-09a External audit by COA: from submission of accounts to the annual reports

Source: atlas diagram 09a (09a_audit_sequence.mmd). Actors: Chief accountant (head of the accounting unit), COA audit team, Head of agency or authorized official, COA Cluster or Regional Director, COA Commission Proper, President.

Basic course:

- 1. Accounting unit to COA audit team: Accounts: paid vouchers with the daily reports of payments, journal entries, reports. Year-end statements by 14 February
- 2. COA audit team: Audit: financial (are the statements fairly presented), compliance (were the rules followed), performance (were results achieved with economy)
- 3. COA audit team to Head of agency: Audit Observation Memorandum on each finding
- 4. Head of agency to COA audit team: Comments, explanations, documents
- (choice: Finding on a transaction: a requirement is missing)
- 5. COA audit team to Head of agency: Notice of Suspension. The amount is suspended until the requirement is met
- (choice: Persons liable comply)
- 8. Head of agency to COA audit team: Requirement met, or amount returned
- 9. COA audit team to Head of agency: Notice of Settlement
- 14. COA audit team to Head of agency: When a decision is final: Notice of Finality of Decision. The agency records a receivable from the persons liable. Then COA Order of Execution (for example, withholding of pay)
- 15. COA audit team to Head of agency: Each quarter: Statement of Audit Suspensions, Disallowances and Charges
- 16. COA audit team to Head of agency: Draft findings discussed. Then the audit report of the agency: opinion on the statements, observations and recommendations, status of earlier recommendations
- 17. Head of agency to COA audit team: Action plan on the recommendations
- 18. COA audit team to President: COA annual report on the financial condition and operation of the government, by 30 September

Alternate courses:

- Instead, when: Finding on a transaction: illegal, irregular, unnecessary, excessive or extravagant expense: 6. COA audit team to Head of agency: Notice of Disallowance, naming the persons liable
- Instead, when: Finding on revenue: under-assessment or under-collection: 7. COA audit team to Head of agency: Notice of Charge, naming the persons liable
- Instead, when: Persons liable contest: 10. Head of agency to COA directors: Appeal 11. COA directors to Head of agency: Decision 12. Head of agency to COA Commission Proper: Petition for review 13. COA Commission Proper to Head of agency: Decision of the Commission Proper

### BUC-10b Collection of taxes and customs duties: from the taxpayer to the Treasury Single Account

Source: atlas diagram 10b (10b_tax_and_customs_collection_sequence.mmd). Actors: Taxpayer or importer, Authorized agent bank or payment gateway, BSP.

Basic course:

- 1. Taxpayers and importers to eFPS and eBIRForms: File the return electronically
- 2. Taxpayers and importers to Agent banks and gateways: Pay: bank debit, online gateway, at a bank branch, or to a revenue collection officer where there is no bank
- 3. Agent banks and gateways to Taxpayers and importers: Payment confirmation
- 4. Agent banks and gateways to eFPS and eBIRForms: Report of payments received
- 5. eFPS and eBIRForms: Post the payment to the taxpayer account
- 6. Taxpayers and importers to E2M customs system: Goods declaration
- 7. E2M customs system to Taxpayers and importers: Assessment of duties and taxes
- 8. Taxpayers and importers to Agent banks and gateways: Pay the assessed amount
- 9. Agent banks and gateways to Payment Application Secure: Abstract of collection, encrypted and authenticated
- 10. Payment Application Secure to E2M customs system: Confirmed payment
- 11. E2M customs system to Taxpayers and importers: Release of the goods
- 12. Agent banks and gateways to Treasury Single Account: Remit collections to the account of the Treasury, daily
- 13. Agent banks and gateways to eTRAMS: Report of collections to BTr
- 14. eTRAMS: Monitor collections and disbursements (eTRAMS)
- 15. eTRAMS to eFPS and eBIRForms: Compare remittances with collection reports
- 16. eTRAMS to E2M customs system: Compare remittances with collection reports

### BUC-10d A tax refund: how money collected as tax is paid back

Source: atlas diagram 10d (10d_tax_refund_sequence.mmd). Actors: Taxpayer or importer, BIR office or approving official, DBM (bureaus and approving officials), Bureau of the Treasury, COA.

Basic course:

- 1. Taxpayers and importers to BIR: Claim for refund with documents. Kinds: input VAT on zero-rated sales, tax collected by error, excess creditable withholding tax, conversion of a tax credit certificate into cash
- 2. BIR: Verify the claim within the time limit (180 days for regular claims, 90 days for VAT claims)
- 3. BIR to BIR: Recommendation
- 4. BIR to Taxpayers and importers: Decision: grant in full, grant in part, or deny. A denied claim may go to the tax court
- 5. BIR to DBM: Request for release against the amount for tax refunds. VAT refunds: not more than 5 percent of last year's VAT collections of BIR. Other refunds: from the collections of the current year
- 6. DBM to BTr: Release. The amount is treated as trust receipts
- 7. BTr to Taxpayers and importers: Refund paid
- 8. BIR: Collection report adjusted for the refunds of the current year and of earlier years (net collections)
- 9. BIR to DBM: Quarterly financial and physical reports through URS
- 10. COA to BIR: Audit of the refunds
- 11. BIR to BTr: End of year: the unused balance reverts to the unappropriated surplus of the General Fund

### BUC-11b Cash programming: how the amount of cash authority for a period is decided

Source: atlas diagram 11b (11b_cash_programming_sequence.mmd). Actors: DBCC, DBM (bureaus and approving officials), Bureau of the Treasury, Agency as a whole (central office), Department of Finance, Servicing bank, BSP, Authorized agent bank or payment gateway.

Basic course:

- 1. DBCC to DBM: Fiscal program of the year: revenue, disbursements, deficit, financing
- 2. DBCC to BTr: Same fiscal program, with the financing program
- 3. National agency to DBM: Monthly Disbursement Program (BED 3) through URS
- 4. DBM to BTr: Disbursement program of the government, by month
- 5. DOF to BTr: Revenue forecast, by month
- 6. BTr: Cash forecast for the next three months, updated regularly
- 7. BTr: Plan the borrowing schedule and the placement of surplus cash
- 8. DBM to Servicing banks: NCA for the quarter, per agency, by month
- (repeated: Every working day)
- 9. Servicing banks to BTr: Payments made on agency orders
- 10. BTr to Treasury Single Account: Replenish the servicing banks
- 11. Agent banks and gateways to Treasury Single Account: Collections of BIR and BOC arrive through collecting banks
- 12. BTr: Check the cash balance against the forecast
- 13. National agency to DBM: Monthly Report of Disbursements (FAR 4)
- 14. DBM: Compare actual payments with the program
- 17. BTr to DBCC: Monthly Cash Operations Report: revenue, disbursements, surplus or deficit, financing

Alternate courses:

- Only when: Agency spends slower than its program, or cash is not sufficient: 15. DBM to National agency: Later NCAs adjusted to spending performance and to the fiscal position
- Only when: Agency needs more cash than its program: 16. National agency to DBM: Request for additional NCA, with justification

### BUC-11d One foreign project loan: approvals, signing, use of the loan and repayment

Source: atlas diagram 11d (11d_foreign_loan_sequence.mmd). Actors: Agency as a whole (central office), ICC, DBM (bureaus and approving officials), Department of Finance, Monetary Board, Office of the President, Dealer or lender, Department of Justice, Bureau of the Treasury.

Basic course:

- 1. National agency to ICC: Project proposal for ICC review
- 2. ICC to National agency: ICC recommendation, ED Council approval
- 3. National agency to DBM: Request to provide for the project in the budget
- 4. DBM to DOF: Forward Obligational Authority (project loan)
- 5. DOF to Monetary Board: Request for approval in principle of the loan terms
- 6. Monetary Board to DOF: Approval in principle
- 7. DOF to Office of the President: Request for Special Authority, at least 10 working days before the date needed, with: agency letter, draft loan agreement, Monetary Board concurrence, statement of compliance with laws, Forward Obligational Authority
- 8. Office of the President to DOF: Special Authority (or Full Powers) to negotiate and sign
- 9. DOF to Dealers and lenders: Negotiation. Loan documents cleared by the inter-agency committee that reviews foreign loan documents
- 10. DOF to Dealers and lenders: Loan agreement signed
- 11. Monetary Board to DOF: Final approval of the loan terms
- 12. DOJ to DOF: Legal opinion on the authority of the borrower
- 13. Dealers and lenders to DOF: Loan declared effective
- (choice: Direct payment)
- 14. National agency to Dealers and lenders: Withdrawal application, after the delivery is accepted and the bill is approved. The agency records the asset and a payable
- 15. Dealers and lenders: Pays the supplier directly
- 16. BTr to National agency: Journal entry voucher of BTr: the lender has paid. BTr records the subsidy to the agency and the loan
- 17. National agency to DBM: Copy of that voucher and the list of suppliers paid
- 18. DBM to National agency: Non-Cash Availment Authority. The agency closes the payable against Subsidy from National Government
- 21. BTr to Dealers and lenders: Interest and principal on the due dates, from the Treasury Single Account. Only the books of BTr record them: principal reduces the loan payable, interest is an expense

Alternate courses:

- Instead, when: Cash through the Treasury: 19. Dealers and lenders to BTr: Loan proceeds to the Treasury. BTr records cash and Loans Payable-Foreign on the credit advice of BSP 20. DBM to National agency: NCA under the MDS sub-account for foreign-assisted projects

### BUC-12a Personnel spending: from an authorized position to the monthly payroll and the remittances

Source: atlas diagram 12a (12a_position_to_payroll_sequence.mmd). Actors: Personnel officer, Head of agency or authorized official, Employee, Civil Service Commission, Head of the budget unit, Chief accountant (head of the accounting unit), Servicing bank, Remittance receivers: BIR, GSIS, PhilHealth, Pag-IBIG.

Basic course:

- 1. GMIS to Personnel unit: Approved staffing pattern: positions, classification, salary grades
- 2. Personnel unit to GMIS: Monthly update of the plantilla of personnel in GMIS (PSIPOP): filled and vacant positions
- 3. Head of agency to GMIS: Approval of the update in GMIS (second approver)
- 4. GMIS: Personnel budget of the next year computed from the FILLED positions in GMIS
- 5. Head of agency to Employees: Appointment to a vacant, funded position
- 6. Personnel unit to CSC: Appointment papers for attestation
- 7. CSC to Personnel unit: Attested appointment
- 8. Personnel unit to Budget unit: Payroll, prepared in advance: gross pay, deductions and net pay of each employee. An authorized official certifies: services duly rendered (Box A)
- 9. Budget unit: Budget unit: obligation request. Head of accounting certifies: documents complete, cash available (Box B). Journal entry: salary expense, and the amounts due to BIR, to the insurance bodies and to the employees
- 10. Budget unit to Head of agency: Payroll for approval
- 11. Head of agency to Budget unit: Approved for payment (Box C)
- 12. Accounting unit to Servicing banks: Payment order for the net pay: to the accounts of the employees, or as an advance to the disbursing officer who pays in cash
- 13. Servicing banks to Employees: Net pay. For cash: each employee signs the payroll, and the disbursing officer certifies that each one was paid (Box D)
- 14. Employees to Personnel unit: Reports of attendance, after the payroll. An overpayment for an absence without pay is demanded back
- 15. Budget unit to GSIS, PhilHealth, Pag-IBIG: Tax withheld (by Tax Remittance Advice), premiums and contributions of employee and government

Alternate courses:

- Only when: Shortage in one personnel benefit: 16. Head of agency to Budget unit: Advice for use of PS Allotment (APSA)

### BUC-14a Budget cycle of a local government unit (province, city or municipality) under the Local Government Code

Source: atlas diagram 14a (14a_lgu_budget_sequence.mmd). Actors: Local chief executive, Local finance committee, Agency as a whole (central office), Local treasurer, accountant and budget officer, Sanggunian, Bureau of the Treasury, COA.

Basic course:

- 1. Local chief executive to Local finance committee: Annual investment program from the approved local development plan
- 2. Local finance committee to Local chief executive: Income estimate and recommended spending ceiling by sector, based on the approved local plans
- 3. Local chief executive to National agency: Budget call with the ceilings
- 4. Local treasurer to Local chief executive: Statements of income and expenditures
- 5. National agency to Local chief executive: Budget proposals, on or before 15 July
- 6. Local chief executive to Local finance committee: Review and budget hearings
- 7. Local chief executive to Sanggunian: Executive budget, not later than 16 October
- 8. Sanggunian: Enact the appropriation ordinance on or before the end of the current fiscal year, within the legal limits (see 14b)
- 9. Sanggunian to Local chief executive: Ordinance for approval
- (choice: No ordinance at the start of the fiscal year)
- 10. Sanggunian: Stay in session, with no other business. After 90 days the ordinance of the previous year is deemed reenacted, only for salaries, statutory and contractual obligations, and essential operating expenses
- 11. Sanggunian to Sanggunian: Copy of the ordinance. DBM reviews provinces, highly urbanized cities, independent component cities, and municipalities in Metro Manila. The provincial sanggunian reviews component cities and municipalities
- (choice: No action within 90 days)
- 12. Sanggunian to Sanggunian: The ordinance is deemed reviewed and stays in full force
- 14. Local treasurer: Release allotments. Collect local taxes and fees
- 15. BTr to Local treasurer: National Tax Allotment released automatically and directly to the treasurer (BTr)
- 16. Local treasurer: Before each payment: budget officer certifies the appropriation, accountant obligates it, treasurer certifies available funds
- 17. National agency to Local chief executive: Voucher certified and approved by the head of the department. The local chief executive also approves it, except for regularly recurring administrative expenses (payrolls, utilities, remittances)
- 18. Local treasurer to eSRE: Statement of receipts and expenditures to BLGF (eSRE), quarterly and annual. Accounts to COA
- 19. COA to Local chief executive: COA audit report

Alternate courses:

- Instead, when: Items exceed the legal limits: 13. Sanggunian to Sanggunian: Ordinance declared inoperative in whole or in part. The treasurer may not pay from those items

### BUC-14f The budget of a barangay: who prepares, who enacts, who reviews

Source: atlas diagram 14f (14f_barangay_budget_sequence.mmd). Actors: Barangay officials, Local treasurer, accountant and budget officer, Sanggunian.

Basic course:

- 1. Barangay to Barangay: Estimate of income for the next year, and statements of income and expenditure, on or before 15 September
- 2. Barangay: Prepare the budget with the treasurer. Mandatory items: 10 percent of the general fund for the youth council, at least 20 percent of the tax allotment for development, 5 percent of regular income for calamities. Personal services at most 55 percent of last year's income
- 3. Barangay to Barangay: Budget, on or before 16 October
- 4. Barangay: Appropriation ordinance, by a majority of all members. The punong barangay votes only when the votes are equal and has no veto
- 5. Barangay to Local treasurer: Ordinance, within 10 days after enactment
- 6. Local treasurer to Sanggunian: Ordinance with findings
- 7. Sanggunian: Review within 60 days: legal requirements and limits are met, appropriations do not exceed estimated income
- (choice: No action within 60 days)
- 8. Sanggunian to Barangay: The ordinance is deemed to be in full force
- 10. Barangay: Custody of the funds. Collections and payments
- 11. Barangay to Local treasurer: Records of transactions. The accounts are kept in the offices of the barangay treasurer and of the city or municipal accountant

Alternate courses:

- Instead, when: Found inoperative, in whole or in part: 9. Sanggunian to Barangay: Returned for adjustment. The treasurer may make no further payments from the inoperative part

### BUC-15a Government corporations (GOCCs): corporate operating budget, budgetary support and reports

Source: atlas diagram 15a (15a_gocc_budget_sequence.mmd). Actors: GOCC management, GOCC governing board, DBM (bureaus and approving officials), Congress, Bureau of the Treasury, COA, GCG.

Basic course:

- 1. GOCC management to GOCC board: Proposed COB
- 2. GOCC board to GOCC management: Board approval
- 3. GOCC management to DBM: COB on or before 31 March, with DBM Forms 700, 703-A to 703-C, 705, 706
- 4. DBM: Evaluate: uses agree with the board approval, sources cover uses, national priorities, physical performance, use of last year's budget, financial ratios
- 5. DBM to GOCC management: COB approval letter (within 20 working days)
- 6. GOCC management to DBM: Request for subsidy or equity in the national budget proposal
- 7. Congress to DBM: GAA item "Budgetary Support to Government Corporations"
- 8. GOCC management to DBM: Special Budget Request. The amount must be in the board-approved COB
- 9. DBM to BTr: Release document
- 10. BTr to GOCC management: Cash released directly to the corporation
- 12. GOCC management to BTr: Dividends: at least 50 percent of annual net earnings
- 13. GOCC management to DBM: Quarterly financial and physical reports through URS, within 30 days after each quarter. Also published on its website
- 14. GOCC management to Congress: Written notice that the reports were submitted and published
- 15. GOCC management to COA: Year-end financial statements by 14 February
- 16. COA to GOCC board: Audit report
- 17. GCG to GOCC board: Performance targets and evaluation of the corporation

Alternate courses:

- Only when: The corporation owes the Treasury: 11. BTr: Offset the release against dividends due, guarantee fees, advances and other receivables

### BUC-15b Transfer of funds from one agency to another body that will implement

Source: atlas diagram 15b (15b_inter_agency_transfers.mmd). Actors: Agency as a whole (central office), Implementing body that receives transferred funds, Supplier or contractor, DBM (bureaus and approving officials), COA.

Basic course:

- 1. National agency to Implementing body: Memorandum of agreement: purpose, amount (enough for three months, or the total project cost), period, reports
- 2. National agency: Obligation recorded against its own allotment
- 3. National agency to Implementing body: Check in the name of the implementing body. The receiver issues an official receipt
- 4. National agency: Books: Due from National Government Agencies (a receivable). Not yet an expense, not yet a disbursement in the budget reports
- 5. Implementing body: Trust fund books: Due to NGAs (a liability). The money goes to a trust account, or to the Treasury, from which DBM gives an NCA for trust
- 6. Implementing body to Suppliers and payees: Procurement, contract
- 7. Suppliers and payees to Implementing body: Delivery, inspected and accepted
- 8. Implementing body to Suppliers and payees: Payment from the trust account or under the NCA for trust
- 9. Implementing body to National agency: Within ten days after each month: reports of checks issued and of cash disbursements, approved by the head of the implementing body
- 10. National agency: Books: expense recorded, receivable reduced. Now reported as disbursed. The implementing body reduces its liability by the same expenses
- 12. National agency to DBM: FAR 1-C each quarter: obligations, disbursements, liquidations and balances of fund transfers
- 13. COA to National agency: The auditor of the implementing body audits its payments. The auditor of the source agency audits the transfer

Alternate courses:

- Only when: Money remains at the end of the project or of the validity period: 11. Implementing body to National agency: Unused balance returned, if the agreement says so

### BUC-15f Cash aid to persons: from the list of beneficiaries to the credit in each account

Source: atlas diagram 15f (15f_cash_aid_to_persons_sequence.mmd). Actors: Congress, Program office of an agency that pays cash aid, DBM (bureaus and approving officials), Government bank or remittance institution, Household or beneficiary, COA.

Basic course:

- 1. Congress to Program office: Program law: who qualifies, conditions, kinds of grant. Budget law: the amount for the year
- 2. Program office: Select households with a standardized targeting system. Check the list again every three years
- 3. Program office: Amount of each grant, as fixed by the advisory council of the program and reviewed every six years
- 4. Program office: Check that each household met the conditions (for example school attendance, health visits)
- 5. Program office: Payroll of beneficiaries for the period, certified and approved. Obligation recorded against the allotment
- 6. DBM to Program office: Cash authority (NCA) for the period (chapter 05)
- 7. Program office to Payment agents: Payment order with the list of accounts, within the cash authority
- 8. Payment agents to Beneficiaries: Grant credited to the account of the household, or paid out by a remittance institution
- 9. Payment agents to Program office: Report of amounts credited and of amounts not credited
- 10. Program office: Accounting entries. Amounts not credited are returned or paid again
- 11. Program office to Congress: Yearly report on the program, before the President's budget message
- 12. COA to Program office: Independent monitoring committee, and audit by COA

### BUC-16f Public verification of DBM release documents with a blockchain record

Source: atlas diagram 16f (16f_document_verification_blockchain.mmd). Actors: DBM (bureaus and approving officials), Agency as a whole (central office), Any person.

Basic course:

- 1. DBM to ADRS: Approved release document (SARO, or advice of NCA)
- 2. ADRS to Document verification (blockchain): Record of the issued document
- 3. Document verification (blockchain): Store a fingerprint of the document (a hash) with date and document number. The record cannot be changed later
- 4. ADRS to National agency: Document for download, with a QR code
- 5. National agency to Any person: Copy of the document (for example to a contractor or a bank)
- 6. Any person to Document verification (blockchain): Scan the QR code, or enter the document reference
- 7. Document verification (blockchain) to Document verification (blockchain): Retrieve the record
- 8. Document verification (blockchain) to Document verification (blockchain): Stored record
- 9. Document verification (blockchain) to Any person: Result: the copy matches the issued document, or it does not
