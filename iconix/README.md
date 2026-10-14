# ICONIX models

These files are made by `tools/build.py` from the registers `use_cases.csv`, `transitions.csv`, `bindings.csv`, `place_holders.csv`, `records.csv`, `fields.csv` and `record_links.csv` of `model/`, and from the sequence diagrams of the atlas.

| File or folder | What it holds |
|---|---|
| `domain_model.puml` | Domain model: the records of diagram 17c of the atlas, with their fields and links. |
| `use_case_diagram.puml` | The system use cases of the curated chains and their actors. |
| `robustness/` | Robustness diagrams. `UC-SP-4_B` is use case UC-SP-4 in cohort B; `UC-CO_PE` is use case UC-CO in cohorts P and E, which are drawn once because the use case is the same in both. |
| `sequence/` | Sequence diagrams, with the same names. |
| `USE_CASES.md` | Text of the system use cases and of the business use cases. |

Each `.puml` file is PlantUML text. The `.svg` files are its drawings, made when the build finds PlantUML (see the main README). You can also paste a `.puml` file into any PlantUML tool.

How the objects are chosen. The actor is the role of the transition. The boundary object is what the actor touches in that cohort: a paper form in cohort P, a screen of BTMS in cohort B. The control object is the check of the step, done by a person, by software or by the bank; when the sources do not say who checks, the label says so. The entity objects are the records that the step uses or writes, with the system or body that holds them in that cohort.

The build checks every robustness diagram against the four rules of ICONIX: an actor connects only to boundary objects; a boundary object connects only to actors and control objects; an entity object connects only to control objects; control objects connect to boundary objects, entity objects and other control objects.

Do not edit the files of this folder by hand, except this one: the build writes them again.
