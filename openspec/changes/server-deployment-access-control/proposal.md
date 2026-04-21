## Why

HappyTorch has been moved onto a server, but the repository and deployment guidance still center on Docker-based startup paths that are no longer the intended operating model. At the same time, the web app already has a basic account system, yet anonymous users can still browse problems and submit code, which conflicts with the goal of offering remote practice only to registered users.

## What Changes

- Remove Docker-specific deployment paths from the supported workflow and define direct server deployment as the primary operating model for the web practice service.
- Update deployment documentation and startup expectations for running the FastAPI web app on a server with persistent storage and remote browser access.
- Tighten authentication and authorization so unregistered or signed-out visitors cannot use the practice experience.
- Improve the account lifecycle around registration and login so remote users have a clearer, more reliable sign-in flow and session behavior.
- Preserve per-user drafts, progress, and resume behavior for authenticated users after the server deployment transition.

## Capabilities

### New Capabilities
- `server-deployment`: Define the supported non-Docker server deployment flow, required runtime configuration, and persistence expectations for remote web practice.
- `account-gated-access`: Define mandatory registration/login and enforce authenticated access across the web practice workflow.

### Modified Capabilities

None.

## Impact

- Affected code: `README.md`, `README_CN.md`, `Makefile`, `start_web.py`, `web/app.py`, `web/persistence.py`, `web/static/app.js`, `web/static/index.html`, `web/static/styles.css`
- Affected deployment assets: `Dockerfile`, `docker-compose.yml`, `docker-compose.jupyter.yml`, `entrypoint.sh`
- Affected APIs: `/api/auth/*`, `/api/tasks*`, `/api/random`, `/api/progress`, `/api/submit`, `/api/reset`
- Affected system behavior: server deployment/runbook, account creation/login UX, anonymous access control, session handling, persisted user progress
