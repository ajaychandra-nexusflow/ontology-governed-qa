# Ontology modeling pattern

## Classes

| Class | Purpose | Example |
|---|---|---|
| `odp:Concept` | Governed business term | `odp:Travel`, `odp:Subsistence` |
| `odp:ExpenseCategory` | Source-system category/code | `odp:AIR`, `odp:HOTEL`, `odp:RAIL` |
| `odp:Binding` | Concept → table/column/range | Travel → `gold.fact_expense_line` |
| `odp:Metric` | Single-source measure | `odp:TravelSpend` |
| `odp:CrossProductMetric` | Compound measure with `hasLeg` | `odp:TravelBudgetVariance` |
| `odp:Rule` | Governance policy | `odp:TravelVarianceComparison` |
| `odp:DataProduct` | Business domain grouping | expense product, FP&A product |

`odp:` is a placeholder namespace. Use your own IRI base; keep the class names if you reuse the bundled checker's defaults.

## Properties

| Property | Purpose |
|---|---|
| `odp:includesCategory` / `odp:excludesCategory` | Concept membership |
| `odp:bindsConcept` | Binding → concept |
| `odp:targetTable`, `odp:categoryColumn` | SQL mapping for transactional facts |
| `odp:glFrom`, `odp:glTo` | SQL mapping for ranged accounts (budgets) |
| `odp:appliesConcept` | Metric → concept |
| `odp:hasLeg` | Components of a cross-product metric |
| `odp:governedBy` | Metric → rule |
| `skos:altLabel` | Synonyms the grounder can match |

## Modeling steps

1. List the terms people argue about (where two analysts get different numbers).
2. For each, write a one-sentence definition, synonyms, and what it includes and explicitly excludes.
3. Bind it: table, column, codes or ranges. One binding per source.
4. Define metrics, then cross-product metrics with legs (spend leg + budget leg).
5. Attach a rule to each metric: status filter, scenario filter, treatment of a missing side, what is reported separately.
6. Declare shared identities (for example cost centre) so legs from different sources join on one key.
7. Add SHACL shapes for required properties (every concept has a binding; every binding has a table).

## Rule checklist (budget variance)

- Only approved claims count as spend.
- Only the baseline budget scenario counts, not forecast, unless the question asks to compare scenarios.
- No spend against a budget means spend of 0, not a division artefact.
- Spend with no budget is reported separately, not buried in totals.

## OWL 2 RL inferences worth materializing

- `TravelExpenseLine`: expense line whose category the Travel concept includes
- `ApprovedExpenseLine`: claim status is Approved
- `GovernedTravelExpenseLine`: travel line and approved
- `PlanBudgetLine`: budget line with scenario Plan
- Property chain `claimedBy` ∘ `memberOf` → `claimantCostCentre`

Materialize the closure once and cache it, because start-up is slow without a cache. Reconcile reasoner classification counts against SQL counts as a validation step.
