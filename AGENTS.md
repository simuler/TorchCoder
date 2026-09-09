# TorchCoder Agent Guide

## Project Summary

TorchCoder is a self-hosted PyTorch coding practice platform focused on tensor- and model-component implementation tasks. It behaves like a LeetCode-style web app for deep learning topics such as attention, PEFT, diffusion components, inference utilities, decoding strategies, and RLHF losses.

The repository is now **Web-only**:

- The supported user experience is the FastAPI + static frontend web application.
- Local Jupyter/Notebook practice flow has been intentionally removed.
- Task content is still stored in repository-managed `.ipynb` assets under `templates/` and `solutions/`, but those files are now content sources for the web app, not a local notebook runtime.

## Current Product Model

- Brand name: `TorchCoder`
- Primary interface: browser-based authenticated practice UI
- Backend: FastAPI
- Persistence: SQLite
- Runtime language: Python 3.11
- In-browser code execution model: user code is executed server-side in a restricted namespace and then tested against task-specific assertions

## Repository Layout

Top-level directories and files that matter:

- `start_web.py`
  Thin launcher for the FastAPI app. Reads runtime env vars and prints deployment hints.
- `web/`
  The actual web application.
- `web/app.py`
  FastAPI API layer, task asset loading, code execution, solution loading, auth gating.
- `web/persistence.py`
  SQLite schema and persistence helpers for users, sessions, drafts, progress, and current-task resume.
- `web/static/`
  Single-page frontend assets.
- `torch_judge/tasks/`
  Task registry. Each Python module exports a `TASK` dict with metadata, hint, and tests.
- `templates/`
  Per-task starter assets, stored as `.ipynb`.
- `solutions/`
  Per-task reference solutions, stored as `.ipynb`.
- `deploy/`
  Deployment examples such as systemd and Nginx configs.
- `openspec/`
  Change proposals, specs, designs, and task lists.

## Runtime Architecture

High-level flow:

```text
Browser
  -> GET /                -> web/static/index.html
  -> JS bootstraps        -> web/static/app.js
  -> Auth endpoints       -> web/app.py + web/persistence.py
  -> Task list/detail     -> torch_judge.tasks + template/solution asset readers
  -> Code submit          -> web/app.py::_run_tests()
  -> Result persistence   -> web/persistence.py
  -> SQLite               -> TORCHCODER_DB_PATH
```

### Backend Responsibilities

`web/app.py` owns:

- Auth/session HTTP endpoints
- Protected task/progress/submission endpoints
- Reading starter descriptions/code from `templates/*.ipynb`
- Reading reference solutions from `solutions/*_solution.ipynb`
- Executing user-submitted code with a controlled namespace
- Running task-specific tests from `torch_judge.tasks`

Important API endpoints:

- `GET /`
- `GET /api/auth/me`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/tasks`
- `GET /api/tasks/{task_id}`
- `PUT /api/tasks/{task_id}/workspace`
- `GET /api/tasks/{task_id}/solution`
- `GET /api/random`
- `GET /api/progress`
- `POST /api/submit`
- `POST /api/reset`

### Persistence Model

`web/persistence.py` uses SQLite with these main tables:

- `users`
- `sessions`
- `user_task_progress`
- `user_preferences`

Current env/config conventions:

- DB env var: `TORCHCODER_DB_PATH`
- Default DB file: `data/torchcoder.db`
- Session cookie: `torchcoder_session`
- Session TTL env var: `SESSION_TTL_DAYS`
- HTTPS cookie toggle: `SESSION_COOKIE_SECURE`

Important continuity features already implemented:

- Account creation/login
- Session-based auth
- Draft autosave per task
- Best-time / attempts / solved state persistence
- Restore last opened task after login

### Task Model

Tasks are auto-discovered from `torch_judge/tasks/*.py`.

Each task module exports a `TASK` dict that includes:

- `title`
- `difficulty`
- `function_name`
- `hint`
- `tests`
- optionally `category`

The registry is built in `torch_judge/tasks/_registry.py`.

Ordering in the UI depends on:

- category order from `CATEGORY_ORDER`
- difficulty order from `DIFFICULTY_ORDER`

### Task Content Assets

Even though notebook mode was removed, the app still depends on `.ipynb` assets:

- `templates/` provides problem statement, signature, example, and starter code
- `solutions/` provides explanation markdown and reference code

`web/app.py` parses the notebooks as JSON and extracts relevant cells.

This is a deliberate compromise:

- Notebook runtime is gone
- Notebook asset format is still retained
- A future migration away from `.ipynb` would be a separate change, not a bug fix

## Frontend Architecture

The frontend is a static SPA-like page served from `web/static/`.

Main files:

- `web/static/index.html`
- `web/static/app.js`
- `web/static/styles.css`

Frontend responsibilities:

- Show auth-gated landing state
- Load task list and grouped categories
- Load task detail into Monaco editor
- Autosave workspace drafts
- Submit code and render per-test results
- Load and reveal solutions on demand
- Display progress and solved counters

The frontend assumes a login-first workflow. Do not reintroduce guest problem browsing unless that is an intentional product change.

## Supported Local / Deployment Workflows

### Supported

- `python start_web.py`
- `make web`
- systemd deployment via `deploy/torchcoder.service`
- Nginx reverse proxy via `deploy/nginx.simuler.cn.conf`

### Removed On Purpose

- `start_jupyter.py`
- `prepare_notebooks.py`
- Make targets for notebook preparation or notebook launch
- notebook-only judge/progress helpers that previously lived in `torch_judge`

If a future agent sees references to Jupyter/Notebook practice in old discussions or archived changes, treat them as historical unless the user explicitly asks to reintroduce that model.

## Major Completed Change: TorchCoder Rename + Web-Only Cleanup

The most important recent change is:

- `rename-happytorch-to-torchcoder-and-remove-notebook-mode`

Intent:

- Rename all user/operator-facing `HappyTorch` branding to `TorchCoder`
- Remove local notebook workflow
- Keep the web app working from repository assets without a notebook preparation step

### What Changed

Branding/config changes:

- `HappyTorch` -> `TorchCoder` on UI and runtime-facing text
- `HAPPYTORCH_DB_PATH` -> `TORCHCODER_DB_PATH`
- `data/happytorch.db` -> `data/torchcoder.db`
- `happytorch_session` -> `torchcoder_session`
- deployment sample renamed to `deploy/torchcoder.service`

Removed files/modules:

- `start_jupyter.py`
- `prepare_notebooks.py`
- `torch_judge/engine.py`
- `torch_judge/progress.py`
- `templates/00_welcome.ipynb`

Simplified interfaces:

- `Makefile` is web-only
- `torch_judge/__init__.py` is now just a thin export for task registry access

### What Did Not Change

- The web app still reads `.ipynb` task assets
- The package name `torch_judge` was not renamed
- SQLite schema remained compatible
- Existing DB files can still be reused by pointing `TORCHCODER_DB_PATH` to the old file path

### Operational Consequences

- Existing users must log in again after the cookie rename
- Existing SQLite data can survive the rename without migration if the new env var points to the old DB file
- Future work should assume **web-only** unless specs explicitly say otherwise

## Other OpenSpec Context

There are other spec-driven changes in `openspec/changes/`. At the time this guide was written, relevant ones include:

- `server-deployment-access-control`
- `bind-simuler-cn-domain`
- `rename-happytorch-to-torchcoder-and-remove-notebook-mode`

Before doing product-level behavior changes, check whether an active OpenSpec change already defines the expected direction.

## Verification Already Performed For The Web-Only Rename

The completed rename/web-only change was verified with:

- `python -m compileall start_web.py web torch_judge`
- FastAPI `TestClient` flow covering:
  - register
  - task list
  - task detail
  - solution load
  - draft save
  - submit
  - progress
  - logout
- validation that `TORCHCODER_DB_PATH` can point to a legacy SQLite filename
- validation that the session cookie name is now `torchcoder_session`

## Guidance For Future Agents

- Start with `README.md` for product/deployment intent, but use this file for maintenance context.
- Do not reintroduce notebook workflow accidentally when editing docs, Makefile, or startup scripts.
- If changing task content rendering, remember the app parses notebook JSON directly from `templates/` and `solutions/`.
- If changing auth/session behavior, check both `web/app.py` and `web/persistence.py`.
- If changing task ordering or categories, update `torch_judge/tasks/_registry.py`.
- If changing deployment docs or examples, keep `README.md`, `start_web.py`, `Makefile`, and `deploy/` consistent.
- If a user says “the old HappyTorch name still appears”, search for both:
  - `HappyTorch`
  - `happytorch`
- When implementing changes against OpenSpec, read the corresponding files under `openspec/changes/<change>/` before touching code.

## Recommended First Files To Read

For a new agent, the fastest path into the codebase is:

1. `AGENTS.md`
2. `README.md`
3. `web/app.py`
4. `web/persistence.py`
5. `web/static/index.html`
6. `web/static/app.js`
7. `torch_judge/tasks/_registry.py`

That sequence is enough to understand the current product shape before making changes.
