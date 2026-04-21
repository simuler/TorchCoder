## ADDED Requirements

### Requirement: Practice APIs require an authenticated account
The web practice experience MUST require an authenticated account. Any API that exposes task content, user progress, random task selection, solution access, code submission, draft saving, or progress reset SHALL reject unauthenticated requests with an authentication error.

#### Scenario: Anonymous user requests practice data
- **WHEN** an unauthenticated client requests the task list, task detail, progress, random task, or solution endpoints
- **THEN** the server returns an authentication error instead of practice data

#### Scenario: Anonymous user attempts to submit code
- **WHEN** an unauthenticated client submits code or saves a workspace draft
- **THEN** the server rejects the request and does not record any draft or submission state

### Requirement: Registration and login validate credentials consistently
The authentication flow SHALL enforce the configured username and password rules during registration, reject duplicate usernames, reject invalid login credentials, and establish a session for successful registration or login.

#### Scenario: User registers with valid credentials
- **WHEN** a new user submits a username that matches the allowed format and a password that meets the minimum length
- **THEN** the server creates the account, starts a session, and returns the authenticated identity payload

#### Scenario: User registers with a duplicate username
- **WHEN** a user attempts to register with an existing username
- **THEN** the server rejects the request with a conflict error and does not create a second account

#### Scenario: User logs in with invalid credentials
- **WHEN** a user submits an unknown username or incorrect password
- **THEN** the server rejects the login request with an authentication error and does not create a session

### Requirement: Authenticated sessions preserve user continuity
Authenticated users SHALL keep per-account drafts, progress, and last-opened task continuity across browser sessions until logout or session expiry. Invalid or expired sessions MUST be treated as signed out.

#### Scenario: Signed-in user resumes practice
- **WHEN** an authenticated user reloads the web app with a valid session
- **THEN** the app restores the authenticated state and can resume the user’s saved progress and current task context

#### Scenario: User signs out or session expires
- **WHEN** a session is deleted, expired, or no longer valid
- **THEN** the app treats the client as signed out and requires a fresh login before practice features can be used

### Requirement: The web UI blocks unauthenticated practice actions
The web client SHALL present sign-in or registration prompts before practice begins and MUST not expose interactive practice actions to unauthenticated visitors.

#### Scenario: Visitor opens the web app while signed out
- **WHEN** a signed-out visitor loads the HappyTorch web interface
- **THEN** the UI shows account-entry affordances and does not auto-load a usable practice workspace

#### Scenario: Signed-out visitor tries to start a problem
- **WHEN** a signed-out visitor attempts to open a problem or trigger a random task
- **THEN** the UI redirects the visitor into the authentication flow instead of loading the problem workspace
