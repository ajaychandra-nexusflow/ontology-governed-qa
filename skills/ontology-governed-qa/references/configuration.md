# Configuration and security

## Environment variables (names used by the reference implementation)

| Variable | Default | Purpose |
|---|---|---|
| `USE_BEDROCK` | `true` | Use Amazon Bedrock; `false` runs offline mode |
| `AWS_REGION` | none | Region for Bedrock |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | none | Or use a profile / role (preferred) |
| `NOVA_PRO_MODEL_ID` | `us.amazon.nova-pro-v1:0` | Planner/narrator model |
| `TITAN_EMBED_MODEL_ID` | `amazon.titan-embed-text-v2:0` | Embedding model |
| `USE_NEO4J` | `false` | Enable graph features |
| `NEO4J_URI` | `bolt://localhost:7687` | Graph connection |
| `NEO4J_USER` / `NEO4J_PASSWORD` | `neo4j` / none | Set a strong password; never commit it |
| `APP_USER` / `APP_PASSWORD` | none | Web UI credentials; require them, no defaults |
| `SESSION_HOURS` | `8` | Session lifetime |

To use another provider, replace the model client behind the planner, narrator and embedder; the rest of the pipeline is unchanged.

## Amazon Bedrock setup (one example)

1. Enable the chat model and the embedding model in the Bedrock console for your region.
2. Grant `bedrock:InvokeModel` on those model ARNs to the identity that runs the app (least privilege).
3. Prefer an IAM role or profile over long-lived keys.
4. Cross-region model IDs need their prefix (`us.`, `eu.`, `apac.`).

## Optional MCP server

Expose the pipeline to Claude as tools and register it in your client config. Pass secrets via the environment or credential chain, never inline in committed files:

```json
{
  "mcpServers": {
    "ontology-governed-qa": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/mcp_server.py"],
      "env": { "USE_BEDROCK": "true", "AWS_REGION": "<region>" }
    }
  }
}
```

Annotate read-only tools as such and mark anything that writes (graph reload, publishing an extension) as destructive so clients ask for confirmation.

## Security checklist

- All API routes require an authenticated session.
- SPARQL and Cypher consoles are read-only; reject write keywords before they reach the store.
- Uploads and versioning write only to a configured bucket/prefix.
- No default passwords; fail to start if credentials are unset.
- Keep `.env`, keys and tokens out of git (`.gitignore`).

## Troubleshooting

| Symptom | Fix |
|---|---|
| Profile not found | Set explicit credentials or run `aws configure` |
| AccessDeniedException | Enable model access; attach the IAM policy |
| ExpiredTokenException | Refresh the session token |
| Bedrock init failed | Check region and model ID prefix |
| Reasoner slow at start | Use the cached closure file for later starts |
