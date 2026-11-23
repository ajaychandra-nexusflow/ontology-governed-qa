# Architecture

```
Question → Ground → Plan → Validate → Compile → Execute → Narrate → Answer
           embed     LLM    entities   ontology   SQL      LLM      + governance
           + retrieve JSON   resolved   bindings   rows     prose    line + metrics
```

## Roles (swap providers freely)

| Role | Needs | Examples |
|---|---|---|
| Planner / narrator / authoring LLM | Returns strict JSON; respects a vocabulary constraint | Amazon Nova Pro, Claude (Anthropic API or Bedrock), any comparable chat model |
| Embedder | Text embeddings for grounding and question-pattern retrieval | Amazon Titan Text Embeddings V2, any embedding model |
| Ontology store | OWL 2 (Turtle), SPARQL, OWL 2 RL reasoning, SHACL | `rdflib`, `owlrl`, `pyshacl` |
| Governed data layer | Relational tables the compiler can target | SQLite for demos; any warehouse in production |
| Graph (optional) | Connected-data exploration | Neo4j behind a read-only Cypher guard |

## Stage details

**Ground.** Embed the question; retrieve the nearest concept definitions and known question patterns. Cache embeddings (deterministic per text).

**Plan.** Constrain the model to a closed vocabulary: allowed intents, concepts from the ontology, filter fields. Validate output against a schema. A plan is a request, not a query.

**Validate.** Resolve names to master-data keys; map natural dates to fiscal periods; drop or flag unresolved terms. Record whether the plan survived unchanged (used as "plan fidelity").

**Compile.** For each metric leg, read the binding (`targetTable`, `categoryColumn`, included categories, `glFrom`/`glTo`) and the governing rule (status filter, scenario, zero-handling). Emit parameterized SQL. Deterministic and unit-testable.

**Execute.** Read-only connection. Return rows, KPI summary and the SQL text for the audit trail.

**Narrate.** Headline number first. Include items reported separately. Every figure must appear in the rows.

**Governance line.** Concept (with included categories), rule, shared identity key: the visible proof of what was applied.

## Offline mode

With no LLM available the system can still run end to end using hash embeddings, a rule-based planner and template narration. Token and cost metrics read zero. Label offline answers, and optionally withhold them when the LLM path is mandatory.

## Typical latency (illustrative, one question)

| Stage | Range |
|---|---|
| Grounding | 30–50 ms |
| Planning | 0.5–1.5 s |
| Compile | < 10 ms |
| Execute (SQLite) | 50–200 ms |
| Narration | 0.8–2.0 s |
| Total | about 1.4–3.7 s |

Measure your own; these vary with model, region and data size.
