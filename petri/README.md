# Petri nets

These nets are made by `tools/build.py` from the registers `places.csv`, `transitions.csv`, `arcs.csv`, `bindings.csv` and `place_holders.csv` of `model/`, and from the sequence diagrams of the atlas.

| Folder or file | What it holds |
|---|---|
| `chains/` | The curated chains, one net for each chain and cohort (for example `CH-SPEND-B` is the spending chain in cohort B), and `CH-ALL-P`, `CH-ALL-E`, `CH-ALL-B`, which join all the chains through the places they share. |
| `sequences/` | One workflow net for each sequence diagram of the atlas (for example `07a`). |
| `ANALYSIS.md` | Size, start and end of each net; the soundness of each workflow net; and the acts that open a window in which the records of the NCA balance differ. |

Each net is written in three formats. The PNML file is a place/transition net in the standard exchange format for Petri nets (ISO/IEC 15909-2), which many Petri net tools can open. The DOT file is the drawing in the language of Graphviz. The SVG file is the drawing.

Two things are lost in the PNML files, because a place/transition net cannot hold them. A read arc (the transition needs the token and leaves it) is written as two arcs, one in each direction. An arc marked "amount" moves an amount of money in the model, but in the PNML file it moves one token. A coloured Petri net would carry the amount, the UACS code and the fund cluster on the tokens; this repository does not build one.

In the drawings, the colour of a place says its line (blue for authority, green for the claim, orange for cash, grey for records). A double border is a balance, a dashed border is a record on its way between two bodies (named after its flow in the map), and a black dot in the label is a token at the start. A grey box is an act done by software in that cohort.

Do not edit the files of this folder by hand, except this one: the build writes them again.
