# Governance gates for ontology extensions

Flow: **business text → LLM draft (Turtle) → gates → human approval → publish**.

| # | Gate | Needs runtime? | `check_extension.py` |
|---|---|---|---|
| 1 | Turtle parses as valid RDF | no | yes |
| 2 | Only approved vocabulary (`odp:`, `rdfs:`, `rdf:`, `skos:`, `owl:`, `xsd:`) | no | yes |
| 3 | No redefinition of core ontology IRIs | needs core file | yes (`--core`) |
| 4 | Every new concept has at least one binding | no | yes |
| 5 | Referenced categories exist in the data products | yes (master data) | no |
| 6 | Bindings target approved tables and valid GL/code ranges | yes (schema catalog) | no |
| 7 | SHACL shapes conform on the merged graph | needs shapes file + `pyshacl` | yes (`--shapes`) |
| 8 | OWL 2 RL reasoner stays consistent | needs `owlrl` and merged graph | no |

Gates 5, 6 and 8 depend on your live data and reasoner; implement them in the runtime that owns the database.

## Publish step

Only after all gates pass **and** the user approves: write the Turtle to `ontology/extensions/<name>.ttl`, reload the ontology, rebuild the embedding index, refresh the reasoner cache, and optionally version the file (for example to object storage). Keep extensions additive; never overwrite core definitions.

## Typical failures

- A new concept without bindings: add `odp:bindsConcept` from a binding to it.
- A concept reusing a core IRI (`odp:Travel`): choose a new IRI or propose a change to the core through review.
- Categories in `includesCategory` that do not exist in the data: confirm codes with the data owner.
