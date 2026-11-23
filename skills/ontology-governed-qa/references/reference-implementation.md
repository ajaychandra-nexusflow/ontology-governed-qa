# Worked example: travel & expense governance

A reference implementation of the pattern (Flask UI, SQLite Gold/Shared layer, OWL 2 ontology, optional Neo4j). All data is **synthetic** and all figures below are illustrative.

## Data model

| Table | Purpose |
|---|---|
| `gold.fact_expense_line` | Claims: charged-to, claimed-by, category, amount, status, date |
| `gold.fact_budget` | Budgets: budgeted-for, scenario (Plan/Forecast), GL account, amount |
| `shared.dim_cost_centre` | Cost centres (shared identity across spend and budget) |
| `shared.dim_employee` | Employees with grade and cost centre |
| `dim_fiscal_calendar` | Fiscal periods, for example FY27-P01 to FY28-P06 |

## Governance in the example

- Concept **Travel** = AIR + HOTEL + RAIL; excludes MEAL and MILEAGE (a separate Subsistence concept).
- Spend binding: `expense_category_code IN ('AIR','HOTEL','RAIL') AND claim_status = 'Approved'`.
- Budget binding: GL range 6100–6199 with `scenario = 'Plan'`.
- Rule `TravelVarianceComparison`: approved claims only, Plan scenario only, no spend = 0, no budget reported separately.
- Policy breach: claim amount above the grade-adjusted category cap.

## Governed vs ungoverned drift (illustrative)

| Mode | Variance | Why |
|---|---|---|
| Governed | +3,130 | Approved claims, Travel categories, Plan budget |
| Ungoverned | +5,670 | All claims, all categories, extra budget lines |
| Drift | 2,540 | Explained by status, category and scenario rules |

## Sample questions

Budget and variance
- What is our travel budget variance by cost centre and fiscal month?
- Which cost centres are over budget on travel?
- Compare Plan vs Forecast travel budget

Policy and compliance
- Which claims breached the travel policy cap?
- What is the claim rejection rate by cost centre?

Spend analysis
- Top spenders on travel by grade
- Which vendors hold the largest share of travel spend?

Definitions and lineage
- What does travel mean?
- How is travel budget variance calculated?
- Show lineage for a cost centre in a fiscal month

## Example answer

```
**Travel spend is 45,230 against a 42,100 budget, over by 3,130 (107 % used).**

- Largest overspend: one cost centre-month (1,250)
- 12 cost centre-months had spend but no budget (4,200), reported separately

Governance: concept odp:Travel (AIR, HOTEL, RAIL), rule odp:TravelVarianceComparison, shared identity odp:CostCentre.
```

## Tool catalog (when exposed over MCP or function calling)

| Group | Tools |
|---|---|
| Q&A | `ask_odp(question, governed, cost_centre, fiscal_month, judge)`, `compare_governed_vs_ungoverned(question, cost_centre, fiscal_month)` |
| Ontology | `list_ontology_concepts`, `get_ontology_node(id)`, `get_ontology_reasoning`, `run_sparql(query, graph)`, `validate_ontology` |
| Data | `preview_table(table, limit)`, `get_dashboard(concept)`, `drill_down(cost_centre, fiscal_month, concept, governed)`, `list_business_scenarios`, `list_reference_data` |
| Audit and metrics | `get_audit_trail(limit)`, `get_metrics_summary`, `run_golden_evaluation(judge, ids)`, `list_golden_cases` |
| Authoring | `generate_ontology_extension(text)`, `check_ontology_extension(turtle)`, `publish_ontology_extension(turtle, name)` |
| Graph | `get_graph_status`, `load_graph`, `search_graph(query, limit)`, `explore_graph(key, depth)`, `find_shortest_path(from, to)`, `list_graph_analyses`, `run_graph_analysis(id)`, `run_graph_cypher(query)` |
| System | `bedrock_check` (live model self-test) |

Mark `publish_ontology_extension` and `load_graph` as destructive; the rest are read-only.

## Graph model

Nodes: CostCentre, Employee, ExpenseLine, BudgetLine, Vendor, Category, FiscalPeriod, Scenario, Grade, Concept.
Relationships: MEMBER_OF, CLAIMED_BY, CHARGED_TO, HAS_CATEGORY, BUDGETED_FOR, INCLUDES, EXCLUDES.
Reasoner inferences become labels such as `:GovernedTravelExpenseLine` and `:ApprovedExpenseLine`.

## Known limitations of the example

- Synthetic data; small golden set with clean phrasing.
- No role-based access beyond basic authentication.
- Optional object-storage versioning is off by default.
- Neo4j integration not validated against a live server in the reference build.

Roadmap ideas: RBAC, CSV/Excel export, scheduled golden runs, ontology diff viewer, alert rules on variance thresholds.
