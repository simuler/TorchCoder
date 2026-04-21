## 1. Deployment Cleanup

- [x] 1.1 Remove unsupported Docker deployment assets and Docker-oriented helper targets that are no longer part of the maintained server workflow.
- [x] 1.2 Update `README.md` and `README_CN.md` to document direct server deployment, including dependency install, notebook preparation, host/port binding, persistent database configuration, remote access, and HTTPS cookie guidance.
- [x] 1.3 Adjust the supported web startup path in `start_web.py` and related repo messaging so the primary run flow matches remote server deployment instead of local-only localhost assumptions.

## 2. Backend Access Control

- [x] 2.1 Harden `web/app.py` so all practice-related endpoints require an authenticated session and return consistent `401` errors for anonymous requests.
- [x] 2.2 Tighten registration/login behavior in `web/app.py` and `web/persistence.py` so credential validation, duplicate-account handling, invalid-login responses, and expired-session handling stay consistent under the stricter auth model.
- [x] 2.3 Verify that authenticated users still keep drafts, progress, submission history, and current-task resume behavior after the authorization changes.

## 3. Frontend Auth Gate

- [x] 3.1 Rework `web/static/app.js` bootstrap so signed-out visitors do not preload or use the practice workspace before authentication succeeds.
- [x] 3.2 Update task open, random selection, solution viewing, submission, autosave, and progress interactions to redirect signed-out users into the login/register flow when the backend returns `401`.
- [x] 3.3 Refresh the signed-out UI copy and states in `web/static/index.html` and `web/static/styles.css` so the web app clearly communicates “register or sign in before practicing.”

## 4. Verification

- [x] 4.1 Run targeted verification for registration, login, logout, task loading, draft autosave, submission, solution access, and progress reset as an authenticated user.
- [x] 4.2 Run anonymous-access checks to confirm protected APIs and UI flows consistently block unregistered usage.
- [x] 4.3 Do a final repository pass to confirm Docker references are removed from supported workflows and the change is ready for `/opsx:apply`.
