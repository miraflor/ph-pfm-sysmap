# The web site of the Philippine PFM Systems Map

## Two pages

GitHub Pages serves the folder `docs/`. The site has two pages, and both are made from the registers of `model/`:

| Page | What it is | Made by |
|---|---|---|
| `docs/index.html` | The research portal: the home page of the site | `tools/portal.py` with `tools/portal_site/` |
| `docs/visualizer.html` | The interactive map and the process nets, as before | `tools/pfmmap/site.py` with `tools/site/` |

The portal has seven parts:

| Part | What it shows | Registers |
|---|---|---|
| Overview | Counts, the parts of the site, and what the models do not show | all |
| Systems map | The interactive map, inside the page | all, through `visualizer.html` |
| Processes | The eight curated chains, act by act for each cohort, with their Petri nets and use cases; the twenty workflows of the atlas, step by step | `chains`, `transitions`, `bindings`, `steps`, `actor_map`, `use_cases`, `flows` |
| Formal models | The Petri nets, the ICONIX diagrams and the static maps, each with its source file (PNML, PlantUML or DOT) | `petri/`, `iconix/`, `maps/` |
| Records & data | Each record with its fields, its links to other records, the flows that carry it and the Petri-net places that hold it | `records`, `fields`, `record_links`, `flows`, `places`, `place_holders` |
| Evidence | Open questions, the claims reviewed one by one, and the sources; for each source, the rows that directly cite it across the basis-bearing registers | `gaps`, `audit/claim_reviews.csv`, `sources`, other registers with `basis` |
| Method | How the outputs are built and checked, and what the checks cannot show | none |

## Links

Every choice that changes what the portal shows is in the address after `#`, so any view can be linked, bookmarked and reached again with the Back button. Examples:

| Address | Shows |
|---|---|
| `index.html#view=records&id=R-NCA` | The Notice of Cash Allocation |
| `index.html#view=processes&chain=CH-SPEND&cohort=B` | The spending chain for cohort B |
| `index.html#view=processes&mode=sequences&seq=05a` | The workflow of diagram 05a |
| `index.html#view=models&kind=iconix&id=uc:UC-SP-1` | The ICONIX diagrams of one use case |
| `index.html#view=evidence&id=source:NBC599` | One source and the rows that cite it |
| `index.html#view=architecture&find=F032` | The map, showing flow F032 |
| `visualizer.html#find=F032` | The same, on the page of the map alone; the identifier remains in the URL |
| `index.html#nets` | An old bookmark: forwarded to `visualizer.html#nets` |

An identifier of the registers in the portal is a link: a record opens the record, a flow or a box opens the map at that flow or box, a source opens the source.

## Rules of the design

1. **One source of data.** Both pages read the CSV registers. The site holds no text about the agencies of its own.
2. **The map is kept.** `tools/site/` gets four small changes only: a link to the portal (which opens at the top level, not inside the frame), a mark that hides the header controls of the map when the map is inside the portal, a shared theme, and the `#find=` link.
3. **Only `docs/` is published.** The SVG drawings are copied to `docs/assets/`. Each build first empties `docs/assets/petri`, `docs/assets/iconix` and `docs/assets/maps`, so that no copy of a deleted drawing stays. Links to sources go to the files in the repository.
4. **No drawing older than its source.** An ICONIX drawing is published only with evidence that it was made from the current `.puml` file:
   - PlantUML writes the source into every SVG it draws (older versions in a comment at the end, newer versions as an encoded `<?plantuml-src …?>`). When the SVG holds its source, the portal compares it with the `.puml` file. Equal: the drawing is shown. Different: the drawing is not shown, and the card says that it is older than its source. This check needs no Java.
   - When the SVG holds no source, the drawing is shown if this build drew it, or if `docs/assets/iconix-render-manifest.json` records the same `.puml` and `.svg` from an earlier checked build.
   - Otherwise only the source is shown. `python tools/verify.py` lists the drawings that are not shown.
5. **Light by default.** Dark only when the reader chooses it. The choice is kept in the browser under the same key (`pfm-theme`) for both pages, and the portal passes it to the map inside it.
6. **Links only where the registers have them.** A flow is linked to a step only through `steps.flows`; a record to another record only through `record_links.csv`; a place to a modelled record holder only through `place_holders.csv`; and an atlas actor to a role only through `actor_map.csv`. The site does not guess links. Source back-references index every register that has a `basis` field; this is a record of declared citations, not independent verification.
7. **No stronger claims.** A check of a model is not a check of a real system.

## Build

From the folder of the repository:

```powershell
python tools/check.py
python tools/build.py
python -m unittest discover -s tests -p "test_portal*.py" -v
node tests/portal_js_regression.cjs   # if Node.js is installed
python tools/verify.py
```

The full build needs Python and Graphviz (`dot`). To draw the ICONIX diagrams again, also set `PLANTUML_JAR` and have Java. `python tools/build.py --page-only` writes the two pages and `docs/assets/` from the drawings that exist, without drawing anything again. `python tools/portal.py` writes the portal only.

Commit `docs/index.html`, `docs/visualizer.html` and `docs/assets/` with the changes of the sources. **When a full build regenerates `maps/` or `petri/` SVGs, stage those alongside their corresponding `docs/assets/` copies.** Do not leave out Graphviz comment-only changes in source files while committing their new published copies; a clean checkout will then fail byte-for-byte verification. To avoid those diffs, first inspect and restore only disposable Graphviz SVG modifications, run `python tools/build.py --page-only` to remirror, and rerun verification. Preserve intended diagram changes. In the settings of the repository, GitHub Pages should serve `main`, folder `/docs`.

## Tests

- `tests/test_portal.py`: the check of drawings against their sources (with made-up SVGs of both PlantUML forms, and a stale one); the build writes the same bytes twice; reading the data writes nothing; every published drawing exists and equals its source; the map page keeps its tabs and has the new link.
- `tests/portal_js_regression.cjs`: runs the script of the portal without a browser. It opens every view, every record, every chain with every cohort, every workflow, every source and every open question, and checks that every internal link points to something that exists in the registers and every drawing button to a file that exists.

- `tests/test_portal_v3.py`: joins actual registers for actor mappings and holders, checks that all portal register payloads equal their CSV source, detects mismatched mirrored SVGs, and parses the patched Petri writer as Python 3.9 syntax.
- Optional: `python tests/portal_browser_playwright.py` exercises desktop/mobile views and theme/navigation in Chromium. It requires the third-party Playwright package and a Chromium installation; this is **not** part of the dependency-free standard build and may be unavailable in restricted environments.

## Limits

- The site does not simulate Petri-net tokens, amounts or time. It shows the drawings and links to the PNML.
- No online PlantUML service is used. A drawing is either checked, or not shown.
- The review of sources does not cover every field, or the state of each system today.
- Some steps of the processes name no flow of the register. They are shown without a flow; none is invented.
- Sources and the date of the registers are a snapshot; agencies may have changed since.
- The search box and the choices inside the map are not in the address of the portal; only a specific item selection through `#find=` is. A `#find=` link keeps the identifier in the address after opening. The portal’s seven-section settings are in its own URL fragment.
