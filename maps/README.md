# Static maps

These maps are made by `tools/build.py` with Graphviz, from the same registers as the interactive page (`docs/index.html`). Each map is an SVG file to look at and a DOT file that you can change and draw again with `dot -Tsvg FILE.dot -o FILE.svg`.

Graphviz places the boxes by itself, so the places differ from the zones of the interactive page. The colours and patterns of the lines are the same: blue for an authority, green for a document, grey for data, orange for money; dotted for paper, dashed when a person enters it, bold for a program interface or a payment network, and a hollow arrow for a plan.

| File | What it shows |
|---|---|
| `L0_institutions.svg` | Institutions and parties. One line for each pair of bodies, with the number of flows between their systems and units. |
| `L1_systems_now.svg` | Systems and units, with the flows that are in use, in use for part, described, or not stated. Plans are left out. |
| `L1_systems_with_plans.svg` | The same, with the planned flows. |
| `L2_modules.svg` | The same, with the modules of the systems that have them. |
| `L1_adjacent.svg` | The flows that touch systems next to PFM, such as the eGov portal. |
| `by_domain/` | One map for each part of PFM: planning and budget, release, procurement, obligation and payment, reporting, assets, revenue, cash and debt, local governments, inside one agency, and the planned connections of the IFMIS. |

Do not edit the files of this folder by hand, except this one: the build writes them again.
