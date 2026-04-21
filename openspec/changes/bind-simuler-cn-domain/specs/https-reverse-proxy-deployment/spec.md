## ADDED Requirements

### Requirement: HTTPS reverse proxy fronts the HappyTorch application
The deployment SHALL place HappyTorch behind an HTTPS-capable reverse proxy that accepts requests for `simuler.cn` and forwards them to the local HappyTorch web process.

#### Scenario: Reverse proxy forwards requests to the app
- **WHEN** the reverse proxy receives a request for `simuler.cn`
- **THEN** it forwards the request to the HappyTorch process running on the configured local host and port

#### Scenario: HTTP requests are normalized to the secure entrypoint
- **WHEN** a browser accesses `http://simuler.cn`
- **THEN** the deployment redirects the request to `https://simuler.cn`

### Requirement: Proxy headers preserve the public request context
The reverse proxy configuration SHALL forward the original host and scheme information needed for operating HappyTorch behind a public domain.

#### Scenario: Proxy sends origin-related headers
- **WHEN** the reverse proxy passes a request to HappyTorch
- **THEN** it forwards the original `Host` header together with `X-Forwarded-Proto` and `X-Forwarded-For`

### Requirement: HTTPS deployments use secure session-cookie settings
HappyTorch SHALL document and support `SESSION_COOKIE_SECURE=true` as the default cookie configuration when the site is exposed at `https://simuler.cn`.

#### Scenario: Operator deploys with HTTPS enabled
- **WHEN** the operator configures HappyTorch for the supported HTTPS domain deployment
- **THEN** the service configuration sets `SESSION_COOKIE_SECURE=true`

#### Scenario: Operator reviews the deployment guide
- **WHEN** the operator follows the documented reverse-proxy deployment steps
- **THEN** the guide explains why secure cookies are required for the HTTPS domain entrypoint
