# Evaluating accuracy

## Online checks (every request)

| Check | Weight | What it tests |
|---|---|---|
| Numeric faithfulness | 40 % | Every number in the answer traces to the query result |
| Plan fidelity | 20 % | The LLM plan survived validation unchanged |
| Governed data returned | 15 % | The query executed and returned rows |
| Answer structure | 15 % | Non-empty, reasonable length, governance line present |
| Planner/embedding agreement | 10 % | Nearest question pattern matches the planned intent |

An optional LLM judge can add relevance, completeness, groundedness and clarity scores. Report them separately from the weighted score above.

## Golden-set evaluation

- Build business questions with **independently computed** SQL ground truth (not produced by the compiler under test).
- Per-case scoring: data 30 %, intent 20 %, headline number 20 %, concept 10 %, entities 10 %, answer terms 10 %.
- A case passes only when intent, concept, entities, data and headline number are all correct.
- Start with about 15 questions; grow toward 50–100 expert-approved cases for production trust, including messy phrasing, synonyms and unresolvable entities.

## What the scores mean

They measure internal consistency and traceability. A pass shows the pipeline behaves as designed, not that the definitions match what finance means. For production use: sign off each rule with its business owner, reconcile headline numbers to trusted reports, schedule golden-set runs, and watch the audit trail for drift.
