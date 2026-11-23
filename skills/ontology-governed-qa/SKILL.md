---
name: ontology-governed-qa
description: Design, build and operate governed natural-language Q&A over structured business data using an OWL 2 ontology. Use when business definitions (what counts as "travel" or "revenue", which budget scenario is the baseline, which claim statuses count) must be applied consistently in LLM-generated answers; when building ontology-driven text-to-SQL where the LLM plans and a compiler writes the SQL; when comparing governed vs ungoverned answers to expose definition drift; when authoring or validating ontology extensions from a business glossary (Turtle, SHACL, OWL 2 RL); or when measuring answer accuracy with a golden set. Not for generic text-to-SQL with no business definitions, or OWL work unrelated to data Q&A.
---

# Ontology-Governed Q&A

Answer business questions from structured data so that **definitions, rules and joins come from a governed ontology, not from the model's guesses**. Every answer is traceable: question → plan → SQL → rows → narrative → governance line.

## Core principles

1. **The LLM never writes SQL.** It returns a constrained JSON plan (intent, concept, filters). A deterministic compiler turns the plan into SQL using bindings stored in the ontology.
2. **Definitions live in the ontology.** Concept membership (included / excluded categories), status filters, budget scenarios and zero-handling are data, not prompt text.
3. **Numbers come only from query results.** The narrator may not introduce a figure that is not in the returned rows.
4. **Every answer shows its governance.** End with a line naming the concept, rule and shared identity applied.
5. **Governance is switchable.** Any question can run governed or ungoverned; the difference is the *drift*.
6. **Extensions pass gates before publishing.** Nothing enters the ontology without validation.
7. **Accuracy claims are modest.** Scores show internal consistency, not business correctness.

## Choose the workflow

| The user wants to... | Do this | Read |
|---|---|---|
| Understand or design the overall system | Explain/produce the pipeline and components | `references/architecture.md` |
| Turn a glossary or policy into an ontology | Model concepts, bindings, metrics, rules | `references/ontology-modeling.md` |
| Add or change a concept safely | Draft Turtle, run gates, publish | `references/governance-gates.md`, `scripts/check_extension.py` |
| Answer a business question | Follow "Answering a question" below | `references/architecture.md` |
| Show why numbers differ | Run governed vs ungoverned and explain drift | below |
| Measure accuracy | Online checks + golden set | `references/evaluation.md` |
| Configure models, graph DB, MCP, security | Provider-agnostic setup | `references/configuration.md` |
| See a complete worked example | Travel & expense reference implementation | `references/reference-implementation.md` |

Load only the reference you need.

## Answering a question

If a tool/MCP server exposing this pipeline is connected (see the tool catalog in `references/reference-implementation.md`), call it. Otherwise follow the stages yourself or design them into the user's code:

1. **Ground.** Retrieve the relevant concept definitions and similar question patterns (embeddings, or keyword match in offline mode).
2. **Plan.** Produce JSON only, limited to the ontology's vocabulary:
   ```json
   {"intent": "variance", "concept": "Travel", "cost_centres": [], "fiscal_months": [], "rationale": "..."}
   ```
3. **Validate.** Resolve entities against master data ("sales EMEA" → `CC200`, "August" → `FY27-P02`). Drop anything that does not resolve; never invent a code.
4. **Compile.** Build SQL from the concept's bindings and the rule's filters. No hard-coded business logic in the compiler.
5. **Execute.** Run read-only SQL against the governed layer.
6. **Narrate.** Lead with the headline number, then the largest drivers, then anything reported separately (for example spend with no budget). Use only returned figures.
7. **Append the governance line**, for example:
   `Governance: concept odp:Travel (AIR, HOTEL, RAIL), rule odp:TravelVarianceComparison, shared identity odp:CostCentre.`
8. **Record metrics** (tokens, latency, cost, accuracy score) in an audit trail.

If planning or validation fails, say so. Do not fall back silently to an unconstrained guess; if an offline fallback was used, label the answer as such (or withhold it when the deployment requires the LLM path).

## Explaining governance drift

Run the same question twice and report both numbers plus the difference and its causes:

- **Governed:** only approved claims, only listed categories, only the baseline budget scenario.
- **Ungoverned:** keyword matching over all rows.
- **Drift:** governed − ungoverned, attributed to the specific rule that explains each part (status filter, category exclusion, scenario filter).

Treat drift as evidence for *why governance matters*, and as a prompt to check the rule with its business owner.

## Authoring an ontology extension

1. Collect the business text: concept name, definition, synonyms, included/excluded categories, target table/column, GL or code ranges, governing rule.
2. Draft Turtle that reuses the core vocabulary only (see `assets/example-extension.ttl`).
3. Run `python scripts/check_extension.py <extension.ttl> --core <core.ttl> [--shapes <shapes.ttl>]` for the offline gates. The remaining gates need the live data and reasoner (see `references/governance-gates.md`).
4. Show the user the Turtle and each gate result. **Do not publish without explicit approval.**

## Guardrails

- **Read-only access.** SPARQL and Cypher consoles reject writes before they reach the store. Table previews are capped.
- **No secrets in chat, files or commits.** Credentials come from the environment or a credential provider. Never ship default passwords; require them to be set.
- **Don't overstate accuracy.** A passing golden set shows the pipeline is consistent. Recommend domain sign-off and reconciliation to trusted reports; recommend growing the golden set toward 50–100 expert-approved cases for production trust.
- **Report gaps separately.** Spend without budget, budget without spend, unresolved entities and excluded rows are shown, not folded into totals.
- **Say what is synthetic.** Sample datasets and illustrative figures are labeled as such.

## Quick reference

| Term | Meaning |
|---|---|
| Concept | A governed business term (Travel) |
| Binding | Mapping from a concept to table/column/range |
| Metric | Single-source measure (Travel Spend) |
| Cross-product metric | Measure combining sources (Variance = spend − budget) |
| Rule | Governance policy attached to a metric |
| TBox / ABox | Ontology schema / instance data |
| OWL 2 RL closure | Materialized inferences that classify rows (governed travel line, approved line, plan budget line) |
| Drift | Governed vs ungoverned difference |
| Golden set | Questions with independently computed ground truth |
