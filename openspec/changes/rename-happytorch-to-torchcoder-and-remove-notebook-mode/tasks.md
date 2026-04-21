## 1. Branding Rename

- [x] 1.1 Update backend, frontend, package comments, and runtime-facing strings so all externally visible `HappyTorch` branding becomes `TorchCoder`.
- [x] 1.2 Rename deployment-facing identifiers and assets to `TorchCoder` naming, including the database-path env var, session cookie name, default database filename, and deploy/service examples.
- [x] 1.3 Do a repository sweep for remaining `HappyTorch` references and remove or rename any that are still externally exposed.

## 2. Notebook Workflow Removal

- [x] 2.1 Delete the local Notebook startup and preparation workflow, including `start_jupyter.py`, `prepare_notebooks.py`, and the related `Makefile` targets.
- [x] 2.2 Remove notebook-only judge/progress helpers from `torch_judge` and eliminate the local JSON progress path that only existed for Notebook practice.
- [x] 2.3 Remove notebook-only documentation and assets that are no longer needed once Web becomes the only supported practice interface.

## 3. Web-Only Practice Alignment

- [x] 3.1 Keep `web/app.py` loading task descriptions, starter code, and solutions directly from repository assets so Web usage does not require any notebook preparation step.
- [x] 3.2 Update Web page branding, auth/session handling, and fallback responses so the runtime experience consistently uses `TorchCoder` naming.
- [x] 3.3 Rewrite the README and deployment guidance around a single Web-only usage path, including how existing operators migrate configuration from the old `HappyTorch` names.

## 4. Verification

- [x] 4.1 Verify the Web app still supports login, task loading, solution loading, draft save, and code submission from a fresh checkout without running any notebook-preparation script.
- [x] 4.2 Verify renamed deployment settings work with an existing SQLite database path and document the expected re-login caused by the session cookie rename.
- [x] 4.3 Run a final repository pass to confirm the change is apply-ready and no supported workflow still points users to local Jupyter Notebook practice.
