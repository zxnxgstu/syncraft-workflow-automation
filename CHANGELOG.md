# Changelog

## 1.0.0 — Portfolio MVP

- redesigned light/dark SaaS interface
- added login and registration
- added JWT access/refresh authentication with rotation
- added user-owned workflow CRUD and cloning
- added visual workflow builder and node inspector
- added manual, webhook and interval schedule triggers
- added transform, HTTP, log, delay and Telegram nodes
- added variable templating with `{{key}}`
- added execution history, outputs and step-level logs
- added dashboard metrics and activity chart
- added workflow templates and integration catalog
- added Docker Compose and CI workflow
- added 12 automated backend tests
- added portfolio and architecture documentation

## 1.1.0 — Visual identity overhaul
- Rebuilt the authentication screen with a distinct creative automation identity.
- Switched the core palette to graphite, acid-lime, mint and coral accents.
- Added subtle aurora, floating-card and signal-line animations.
- Increased typography, icons, controls and workflow node sizing across the app.
- Removed Demo workspace / Portfolio build / technology footer clutter from sign-in.
- Improved API error formatting so FastAPI validation responses no longer render as `[object Object]`.
- Made local demo credentials self-healing when an older Docker database volume already exists.


## 1.2.0 — Connected Systems overhaul
- Rebuilt the login hero around a live animated integration network/orb instead of a generic split SaaS composition.
- Added a sharper clickable Syncraft link-mark and matching high-resolution SVG favicon.
- Kept the browser tab title to simply `Syncraft`.
- Enlarged typography, icons, navigation, cards and controls throughout the application.
- Reworked the dashboard/sidebar/builder surfaces into a distinct connected-control visual language.
- Added subtle star drift, nebula, orbit, integration-chip and workflow-signal animations with reduced-motion support.
- Removed remaining login clutter and preserved only the useful authentication actions.
- Migrated old `demo@syncraft.local` Docker data automatically to `demo@syncraft.dev`.
- Added a backend compatibility alias so stale browser autofill from earlier builds can still sign in.
- Added a regression test for the legacy demo login alias; backend suite now contains 13 passing tests.
