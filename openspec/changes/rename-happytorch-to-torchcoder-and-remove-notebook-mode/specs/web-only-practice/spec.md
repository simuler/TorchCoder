## ADDED Requirements

### Requirement: Web is the only supported practice entrypoint
The project SHALL define the authenticated Web application as the only supported practice interface. Repository documentation, helper commands, and startup entrypoints MUST NOT direct users to a local Jupyter Notebook workflow for solving problems.

#### Scenario: User follows the quick start
- **WHEN** a user reads the primary setup and usage instructions
- **THEN** the instructions direct the user to start and use the Web application rather than Jupyter Notebook or JupyterLab

#### Scenario: Developer inspects repository entrypoints
- **WHEN** a developer looks for supported run commands in the repository root
- **THEN** only the Web-oriented startup path is presented as a maintained practice entrypoint

### Requirement: Web practice does not require notebook preparation
The Web application SHALL load task descriptions, starter code, and solutions directly from repository-managed task assets without requiring a notebook-copy preparation step or a local `notebooks/` workspace.

#### Scenario: Operator starts the Web server from a fresh checkout
- **WHEN** the operator launches the supported Web startup flow on a repository checkout that has not run notebook preparation
- **THEN** the Web app can still serve task descriptions, starter code, and solutions for supported tasks

#### Scenario: Authenticated user opens a problem
- **WHEN** an authenticated user requests a task detail page and its solution data
- **THEN** the Web app returns the task content without relying on a generated local notebook workspace

### Requirement: Notebook-only practice helpers are removed
The repository SHALL not ship Notebook-only practice helpers that are no longer needed once Web-only practice is the supported model, including notebook launch scripts, notebook preparation scripts, and local notebook progress/judge APIs.

#### Scenario: Developer inspects repository tooling
- **WHEN** a developer reviews repository scripts and helper targets after the change
- **THEN** there is no maintained script or helper target whose purpose is to start or prepare a local Notebook practice environment

#### Scenario: Developer inspects the Python judge package
- **WHEN** a developer reviews the Python package exports and modules used for practice entrypoints
- **THEN** Notebook-specific progress tracking and notebook namespace execution helpers are absent from the supported interface
