## Context

HappyTorch currently ships both local Python startup scripts and a Docker-based deployment story. The repository root still contains `Dockerfile`, `docker-compose.yml`, `docker-compose.jupyter.yml`, and `entrypoint.sh`, while the README quick-start and cloud notes prominently describe Docker as a primary path. This no longer matches the intended operating model because the project has already been moved onto a server and is meant to be accessed remotely through the web UI.

The web application already has a usable account foundation: SQLite-backed users and sessions in `web/persistence.py`, auth endpoints in `web/app.py`, and sign-in/register UI in `web/static/app.js`. However, the practice workflow is only partially protected. Anonymous users can still read task metadata, open problem details, request random tasks, view progress summaries, fetch solutions, and submit code. That creates a mismatch between product intent and runtime behavior.

This change is cross-cutting because it affects deployment assets, backend API authorization, client boot flow, and bilingual documentation. It also touches security-sensitive behavior, so making the decisions explicit before implementation is worthwhile.

## Goals / Non-Goals

**Goals:**
- Make direct server deployment the supported path for the web application.
- Remove unused Docker deployment assets and references that would confuse operators.
- Require registration/login before a user can access the practice experience.
- Keep the current SQLite plus signed-cookie session model, while making its behavior stricter and clearer.
- Preserve authenticated-user drafts, progress, and last-opened task continuity.

**Non-Goals:**
- Rework the notebook/Jupyter practice model into a multi-user server product.
- Add email verification, password reset by email, OAuth, or third-party identity providers.
- Replace SQLite with Postgres or add a separate auth service.
- Introduce role-based access control, billing, quotas, or invitation workflows in this change.

## Decisions

### 1. Keep the existing local auth stack and harden it instead of replacing it
The implementation will continue to use the existing SQLite `users` and `sessions` tables plus PBKDF2 password hashing in `web/persistence.py`. Registration and login already exist and satisfy the project’s scale and operational simplicity needs for a single-server deployment.

Rationale:
- The current auth model is already integrated with per-user draft/progress storage.
- Replacing it with a third-party provider or a new dependency would increase migration cost without solving the immediate access-control gap.
- A stricter authorization boundary can be added with minimal schema disruption.

Alternatives considered:
- Introduce OAuth or a hosted identity provider: rejected because it adds deployment complexity and does not match the self-hosted project shape.
- Add a custom admin approval system: rejected for now because the user requirement is simply “registered users only,” not moderated onboarding.

### 2. Enforce authentication at the API boundary for all practice endpoints
Practice endpoints will move from `get_optional_user` to `get_required_user` wherever access to tasks, progress, solutions, or submissions should be restricted. Public endpoints will be limited to static asset delivery and auth lifecycle endpoints such as `/api/auth/me`, `/api/auth/register`, `/api/auth/login`, and `/api/auth/logout`.

Rationale:
- Backend enforcement is the only trustworthy control; front-end-only gating is trivial to bypass.
- Centralizing around the existing FastAPI dependency keeps the change easy to audit.
- Returning consistent `401` responses gives the client a single recovery path.

Alternatives considered:
- Hide controls in the UI but leave APIs open: rejected because anonymous users could still call the endpoints directly.
- Protect only write actions and leave read-only task access public: rejected because the requirement is to block unregistered usage of the practice experience, not only persistence.

### 3. Treat the signed-out web app as an auth gate, not as a degraded guest mode
The web client will no longer auto-load a usable task workspace for anonymous visitors. Instead, it will boot into an account-entry state, open the auth flow when users try to start practicing, and handle `401` responses by clearing local auth state and redirecting back into login/register.

Rationale:
- The current guest mode is structurally embedded in `web/static/app.js` and contributes to the unauthorized usage path.
- A clear gate is easier for remote users to understand than allowing partial browsing and failing later.
- UI alignment with backend auth rules reduces edge cases and misleading states.

Alternatives considered:
- Keep read-only browsing while blocking submissions: rejected because it still exposes the practice catalog to anonymous users.
- Force an auth modal immediately on page load with no surrounding context: partially acceptable, but the implementation should still keep a minimal landing state rather than a blank or broken screen.

### 4. Collapse deployment guidance onto a single maintained server path
The repository will treat Python-based server startup as the maintained deployment flow. Documentation will explicitly cover dependency installation, `prepare_notebooks.py`, `python start_web.py`, required environment variables, host/port binding, persistent DB location, and HTTPS cookie settings. Unused Docker artifacts and Docker-oriented README sections will be removed or rewritten.

Rationale:
- The repository currently communicates two competing deployment stories.
- The target operating model is now a remote server, so the maintenance burden of stale Docker assets is not justified.
- Keeping one documented path lowers operator error and makes auth/session guidance easier to explain.

Alternatives considered:
- Keep Docker files but mark them as deprecated: rejected because the user explicitly wants unused Docker-related assets removed.
- Replace `start_web.py` with a more elaborate process manager setup in-repo: rejected because the repo should document server deployment, not hardcode one hosting stack such as systemd or Supervisor.

### 5. Preserve current data storage semantics during deployment cleanup
User accounts, drafts, progress, and current-task pointers will remain in the existing SQLite database referenced by `HAPPYTORCH_DB_PATH`. This change will document the persistence expectations for server deployment rather than changing the storage backend.

Rationale:
- The user’s main risk is losing existing progress while moving off Docker-centric instructions.
- The current schema already models the required continuity features.
- Avoiding data migration keeps rollout and rollback straightforward.

Alternatives considered:
- Split auth data and progress data into separate stores: rejected as unnecessary complexity for this scope.

## Risks / Trade-offs

- [Risk] Tightening auth on read endpoints may surprise existing users who could previously browse tasks anonymously. → Mitigation: update the UI to make the sign-in requirement explicit and keep auth prompts visible from first load.
- [Risk] Removing Docker assets may break undocumented personal workflows. → Mitigation: position this as a supported-path cleanup in the docs and keep the direct Python startup path simple and explicit.
- [Risk] Remote deployment without HTTPS could expose session cookies if operators miss configuration. → Mitigation: document `SESSION_COOKIE_SECURE=true` prominently for HTTPS deployments and keep the config variable unchanged.
- [Risk] If the frontend still issues anonymous boot-time API calls after backend hardening, the app could look broken. → Mitigation: reorder client initialization so auth state is established before loading protected practice data, and add consistent `401` handling.
- [Risk] Existing sessions created before the change may not line up with stricter UI assumptions. → Mitigation: continue honoring valid session cookies and only force login when the server rejects or expires the session.

## Migration Plan

1. Remove unused Docker deployment files and Docker-specific README/Makefile guidance.
2. Update server startup documentation for direct web deployment, including persistence and HTTPS cookie notes.
3. Harden backend authorization by requiring authenticated users on all practice-related endpoints.
4. Update the web client boot flow to require login before loading or using practice features.
5. Verify that registration, login, logout, resume, draft save, submit, and reset still work for authenticated users.
6. Deploy the updated server build with the existing database path preserved.

Rollback strategy:
- Revert the code and documentation change set if deployment fails.
- Keep the SQLite database file untouched so user data remains recoverable across rollback.

## Open Questions

- Should the signed-out landing state still show a high-level marketing summary of the platform, or is a minimal login-first shell sufficient?
- Do we want to keep local Jupyter instructions in the README as a developer convenience, even though server deployment is now centered on the web app?
