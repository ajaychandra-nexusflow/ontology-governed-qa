# ontology-governed-qa

A Claude skill for building and operating **governed natural-language Q&A over structured business data**. Business definitions ("what counts as travel spend?", "which budget scenario is the baseline?") live in an OWL 2 ontology. The LLM only proposes a constrained plan; SQL is compiled from the ontology's bindings, and every answer ends with a governance line showing which definitions and rules were applied.

**Needs:** nothing to install for the guidance itself. To run the pipeline you need a SQL database, an LLM that can return JSON, and optionally an embedding model, `rdflib`, `owlrl`, `pyshacl` and Neo4j. Everything is provider-agnostic; Amazon Bedrock settings are documented as one example.

## What the skill does

| You ask Claude to... | The skill gives Claude... |
|---|---|
| "Model our business glossary as an ontology" | A concept / binding / metric / rule pattern with SQL mappings |
| "Make our text-to-SQL answers consistent with finance definitions" | The plan → validate → compile → execute → narrate pipeline where the LLM never writes SQL |
| "Why do two answers to the same question differ?" | Governed vs ungoverned *drift* comparison |
| "Let analysts add a new concept safely" | Business text → Turtle draft → 8 governance gates → publish |
| "How accurate is this?" | Online checks per request plus a golden-set evaluation, with honest limits |
| "Show how employees, cost centres and vendors connect" | Optional Neo4j graph loading, exploration, read-only Cypher |

## Install

### Claude Code (plugin marketplace)

```text
/plugin marketplace add <your-github-username>/ontology-governed-qa
/plugin install ontology-governed-qa@ontology-governed-qa
```

### Manual (Claude Code or any client that reads skill folders)

```bash
git clone https://github.com/<your-github-username>/ontology-governed-qa.git
cp -r ontology-governed-qa/skills/ontology-governed-qa ~/.claude/skills/
```

### Claude.ai

Zip the `skills/ontology-governed-qa` folder and upload it under **Settings → Capabilities → Skills**.

## Try it

Ask Claude:

```text
Using the ontology-governed-qa skill, model "Travel = air + hotel + rail, excluding meals and mileage,
approved claims only, Plan budget scenario" as an ontology extension and check it.
```

Or run the bundled gate checker directly:

```bash
pip install rdflib
python skills/ontology-governed-qa/scripts/check_extension.py \
  skills/ontology-governed-qa/assets/example-extension.ttl \
  --core skills/ontology-governed-qa/assets/example-core.ttl
```

## Repository layout

```text
.claude-plugin/            plugin + marketplace manifests
skills/ontology-governed-qa/
  SKILL.md                 entry point Claude reads
  references/              architecture, modeling, gates, evaluation, configuration, worked example
  scripts/check_extension.py   offline governance gates 1-4 (+ optional SHACL)
  assets/                  small example core ontology and extension (Turtle)
```

## Scope and honesty

- Accuracy scores measure **internal consistency and traceability**, not whether a definition matches your finance team's intent. Have a domain owner sign off rules and reconcile headline numbers to a trusted report before relying on answers.
- The worked example (travel & expense) uses synthetic data and illustrative numbers.
- This repo contains the skill (guidance, patterns, checker). It does not ship a hosted service or credentials. Never commit `.env` files, keys or default passwords.

## License

MIT. See [LICENSE](LICENSE).
