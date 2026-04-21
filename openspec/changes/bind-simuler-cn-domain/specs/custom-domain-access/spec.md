## ADDED Requirements

### Requirement: `simuler.cn` routes to the HappyTorch web service
The deployment SHALL allow `simuler.cn` to resolve to the HappyTorch server and route incoming browser traffic for that host to the running web application.

#### Scenario: Browser opens the root domain
- **WHEN** a user visits `https://simuler.cn`
- **THEN** the request reaches the HappyTorch web application instead of a server placeholder page, directory listing, or unrelated service

#### Scenario: Domain points at the deployed server
- **WHEN** an operator follows the supported deployment guide for `simuler.cn`
- **THEN** the guide defines the DNS record and server mapping required for the domain to reach the HappyTorch host

### Requirement: Public origin configuration matches the domain entrypoint
The deployment SHALL define the public origin for the web service as `https://simuler.cn` so that runtime hints and operator-facing configuration consistently reference the domain entrypoint instead of only the internal bind address.

#### Scenario: Operator configures the domain deployment
- **WHEN** the operator sets up the supported domain-based deployment
- **THEN** the documented runtime configuration includes `PUBLIC_ORIGIN=https://simuler.cn`

#### Scenario: Application startup prints access information
- **WHEN** the web service starts with the supported domain configuration
- **THEN** the operator-facing startup guidance points to `https://simuler.cn` as the intended public access URL

### Requirement: Domain deployment includes an explicit validation procedure
The supported deployment workflow SHALL define how operators verify that `simuler.cn` is serving HappyTorch successfully after DNS and proxy configuration are applied.

#### Scenario: Operator performs post-deployment validation
- **WHEN** the domain deployment is completed
- **THEN** the guide includes checks for DNS resolution, HTTP to HTTPS behavior, and successful loading of the HappyTorch site from `simuler.cn`
