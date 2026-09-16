# Syncraft

**Connect. Automate. Run.**

Syncraft is a portfolio-grade workflow automation and API integration platform built with FastAPI, PostgreSQL, React and Docker. It is designed to look and behave like a real modern SaaS product rather than a tutorial CRUD app.

## What it does

Users can create automation workflows, choose how they start, add processing nodes, run them, and inspect every execution.

A typical flow looks like:

```text
Webhook / Manual / Schedule
            ↓
       Transform data
            ↓
        HTTP request
            ↓
      Telegram / Log
            ↓
     Execution history
```

## Included in this build

### Product experience
- connected-systems visual identity with animated network/orbit hero
- full light and dark themes
- responsive sidebar and navigation
- login + registration screen
- dashboard metrics and activity chart
- workflow list with search/filter support
- visual workflow builder
- node inspector and test payload runner
- execution history and detailed log drawer
- reusable workflow templates
- integrations catalog
- settings/security screen

### Workflow engine
- manual trigger
- public webhook trigger with unique per-workflow URL
- interval scheduler
- transform node with `{{variable}}` templating
- HTTP request node
- structured log node
- delay node
- Telegram node:
  - preview mode without credentials
  - real `sendMessage` call when `bot_token` and `chat_id` are configured
- execution status, duration, input/output and step-by-step logs

### Backend
- FastAPI
- PostgreSQL / SQLAlchemy 2
- JWT access + refresh authentication
- refresh-token rotation
- Argon2 password hashing
- user-owned workflows
- REST API + Swagger/OpenAPI
- demo data seeding
- health/readiness endpoints
- 13 automated backend tests

### Dev / delivery
- Docker Compose
- GitHub Actions CI
- Python compile/test friendly structure
- React + TypeScript + Vite frontend
- `.env.example`
- portfolio copy and architecture docs

## Start it

Requirements:
- Docker Desktop
- Docker Compose

From the project root:

```powershell
docker compose up --build
```

Open:
- App: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Readiness: http://localhost:8000/ready

### Demo account

```text
Email:    demo@syncraft.dev
Password: Syncraft123!
```

The login screen is pre-filled with these values. You can also create a new account from the same screen.

## Suggested first demo

1. Sign in with the demo account.
2. Open **Templates**.
3. Use **Webhook Alert Pipeline** or **API Data Sync**.
4. Save the workflow.
5. Click **Test run**.
6. Open **Executions** to inspect logs and output.
7. Toggle the light/dark theme from the top bar.

For a webhook workflow, copy its webhook URL from the builder and POST JSON to it.

## Integration maturity

| Integration | State |
|---|---|
| Generic HTTP / REST APIs | Working |
| Incoming webhooks | Working |
| Interval scheduler | Working |
| Telegram | Working with credentials; safe preview without them |
| Discord | Catalog/demo connection state |
| GitHub | Catalog/demo connection state |
| Google Sheets | Catalog/demo connection state |
| Notion | Catalog/demo connection state |

The catalog entries are intentionally visible because the architecture is meant to be expanded later, but this README does not pretend the unimplemented OAuth integrations are live.

## Architecture

```text
┌─────────────────────────────┐
│ React + TypeScript + Vite   │
│ Dashboard / Builder / Logs  │
└──────────────┬──────────────┘
               │ REST / JWT
               ▼
┌─────────────────────────────┐
│ FastAPI                     │
│ Auth / Workflows / Engine   │
│ Webhooks / Scheduler        │
└──────────────┬──────────────┘
               │ SQLAlchemy
               ▼
┌─────────────────────────────┐
│ PostgreSQL                  │
│ Users / Flows / Runs / Logs │
└─────────────────────────────┘
```

## Run backend tests

From `backend/`:

```powershell
python -m pip install -r requirements-dev.txt
pytest
```

Expected result for this release:

```text
13 passed
```

## Security / production notes

This is a strong portfolio MVP, not a hosted multi-tenant production service. Before exposing it publicly:
- set a long random `JWT_SECRET`
- use HTTPS
- put the API behind a reverse proxy
- restrict CORS
- add rate limiting to authentication and public webhooks
- restrict outbound HTTP destinations to avoid SSRF in a multi-user environment
- store third-party secrets in a dedicated encrypted secret store
- replace interval scheduling with a durable queue/worker setup for high-volume workloads
- add real OAuth flows for Google/GitHub/Notion integrations

## Design direction

The UI uses a distinct connected-systems identity: deep graphite/green surfaces, acid-lime and mint signals, animated orbit/network elements, larger typography, glass-like workflow cards and a cleaner control-surface layout. Motion is deliberately subtle and disabled when the browser requests reduced motion.

## Portfolio

Ready-to-use portfolio copy is in [`docs/PORTFOLIO.md`](docs/PORTFOLIO.md).

