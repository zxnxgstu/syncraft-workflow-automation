# Syncraft architecture

## Core entities

- **User** — authenticated account.
- **Workflow** — user-owned automation definition.
- **WorkflowStep** — ordered executable node with a type and JSON configuration.
- **Execution** — one run of a workflow, including input/output and timing.
- **ExecutionLog** — step-level observability record.
- **IntegrationConnection** — per-user integration catalog state.
- **RefreshToken** — hashed refresh-token record used for rotation/revocation.

## Execution lifecycle

1. A trigger starts the workflow.
2. An `Execution` row is created as `running`.
3. Steps run in position order.
4. Each step adds structured logs.
5. Context is passed from one step to the next.
6. Template expressions such as `{{message}}` resolve from the current context.
7. The execution is finalized as `success` or `failed` with duration and output.

## Trigger types

- **manual** — started from the authenticated API / UI.
- **webhook** — public URL containing a random workflow token.
- **schedule** — lightweight interval scheduler for the portfolio build.

## Extension points

New action nodes can be added in `backend/app/services/engine.py` and exposed in the frontend node catalog. For a larger deployment, move execution to durable workers (Celery/RQ/Arq) and schedule through a persistent queue.
