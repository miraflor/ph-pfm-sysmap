# Reproduce the Philippine PFM Systems Map

The CSV registers in `model/` and imported historical diagram tree in `atlas_extract/` are the inputs. SVG maps, PNML, DOT, PlantUML, the published single-page site, and `REPORT.md` are generated outputs. You do **not** need to scrape websites to regenerate them. Regeneration is deterministic for the fixed inputs and local rendering engine version; graphical layouts may change between Graphviz/PlantUML releases.

## On Windows / PowerShell

```powershell
# In the repository folder
python --version                  # Python 3.9+
dot -V                            # Graphviz must be on PATH
python tools/check.py            # CSV ids, vocab, sources, cross references
python tools/build.py            # all outputs; optional PlantUML SVG rendering
python tools/verify.py           # PNML/XML, DOT/SVG, generated-net soundness, review integrity, rebuilt page checksum
```

If Graphviz is missing, install it from <https://graphviz.org/download/> and start a fresh terminal. If you have a local PlantUML jar, set `$env:PLANTUML_JAR = 'C:\path\to\plantuml.jar'` and have Java on `PATH` **before** the full build. The build writes `.puml` files either way, but without a configured JAR it cannot confirm its PlantUML renderings. Existing SVGs may be stale if a JAR is not configured. `tools/verify.py` checks `.puml` wrappers but does not replace an actual PlantUML compilation.

For a quick HTML-only edit, `python tools/build.py --page-only` refreshes the self-contained `docs/index.html` without modifying other outputs. Open `docs/index.html` directly in the browser or publish `docs/` via GitHub Pages. The local copy of Cytoscape.js is included; fonts have offline fallbacks.

## Linux / macOS

```sh
# Install Graphviz through your package manager; make sure dot is on PATH
python3 tools/check.py
python3 tools/build.py
python3 tools/verify.py
```

## Inputs and their dependencies

| Artifact | Source | Reproducible transformation |
|---|---|---|
| System map: static `.dot` + `.svg` | `model/nodes.csv`, `model/flows.csv`, supporting sources | `tools/pfmmap/maps.py` via Graphviz |
| Interactive map and process nets | All registers; `atlas_extract/atlas_sequences.json`; layouts from Graphviz | `tools/pfmmap/site.py` + `tools/site/` via `tools/build.py` |
| Curated Petri nets `.pnml`, `.dot`, `.svg` | Places, arcs, transitions, bindings, cohorts | `tools/pfmmap/petri.py` |
| Generated workflow nets | The twenty source sequence trees and steps | `petri.build_seq` + exhaustive `petri.soundness` (generated models only) |
| ICONIX `.puml` + optionally `.svg` | Roles, records, fields, use cases and sequences | `tools/pfmmap/iconix.py`; PlantUML renderer optional |
| Evidence labels | `model/sources.csv`, `audit/claim_reviews.csv` | `Model.evidence` + compiled browser panel; `tools/verify.py` checks identifiers |
| Human factual audit | Agency public documents and dated reviewer conclusions | `EVIDENCE_REVIEW.md`; not reproducible without repeating document research |

For an exhaustive **review queue** (not a claim that every fact is verified), run `python tools/verification_inventory.py`; the resulting `audit/verification_inventory.csv` has one row for each of the 167 nodes and 99 flows, coded by evidence type, declared status, and whether it has been individually reviewed.

For external graph analysis (Gephi, NetworkX, and similar tools), `python tools/export_graphml.py` produces `exports/pfm_flows.graphml` from the same registers. A registered flow with an intermediary becomes two directed segments with the same original `flow_id`; neither proves a live application interface.

`docs/index.html` embeds model data and scripts. Commit it along with any input changes so GitHub Pages displays the updated map. The sources in `model/sources.csv` give provenance, not an immutable snapshot of a public page. Some references have no online URL and some web links may later move.

## What the automated tests can and cannot establish

The checks validate CSV relationships; 47 PNML diagrams' bipartite structure and 20 generated sequence nets' soundness; 62 PlantUML source wrappers; DOT parsing and generated SVG structure; a build of the HTML page that reproduces the committed bytes; theme default; and independently reviewed claim IDs with source codes. **They do not validate legal interpretations, production integration, procurement compliance, asset or cash balances, nationwide deployment, or the correctness of the source sequence diagrams.** For numeric cash controls, add a coloured/timed/net-with-amounts formalization and transaction evidence rather than interpreting plain PNML tokens as money.

See `EVIDENCE_REVIEW.md` for review scope and limits. Each audit row is *not* a guarantee about all fields of the corresponding system or flow.
