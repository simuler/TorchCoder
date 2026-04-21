## ADDED Requirements

### Requirement: Server-first deployment guidance
The project SHALL document direct server deployment of the HappyTorch web service as the supported production path. The documented flow MUST cover dependency installation, notebook preparation, web server startup, persistent database location, and remote browser access behind a public host or reverse proxy.

#### Scenario: Operator follows the supported deployment path
- **WHEN** an operator reads the repository deployment guide
- **THEN** the operator can set up the web service on a server without relying on Docker-specific commands or container-only assumptions

#### Scenario: Operator configures persistent account data
- **WHEN** an operator deploys the web service on a server
- **THEN** the deployment guide specifies how to persist the SQLite database path so user accounts, drafts, and progress survive service restarts

### Requirement: Server runtime configuration is explicit
The project SHALL define the runtime settings required for direct server deployment, including host binding, port binding, database path selection, and secure-cookie guidance for HTTPS deployments.

#### Scenario: Service is exposed for remote access
- **WHEN** an operator starts the web service for remote use
- **THEN** the documented startup path specifies how to bind the application to a server-reachable host and port

#### Scenario: Service is deployed behind HTTPS
- **WHEN** the web app is served behind HTTPS
- **THEN** the deployment guide explains how to enable secure session cookies so authentication cookies are not sent over insecure transport

### Requirement: Unsupported Docker deployment assets are removed from the supported workflow
The repository SHALL not present unused Docker assets as an endorsed deployment path for the server-hosted web practice workflow.

#### Scenario: User checks the primary run instructions
- **WHEN** a user reads the quick start and deployment sections
- **THEN** the instructions point to the direct server startup flow instead of Docker Compose or image-based startup

#### Scenario: User inspects repository deployment helpers
- **WHEN** a user looks for deployment entry points in the repository
- **THEN** only the maintained server deployment path remains part of the supported workflow
