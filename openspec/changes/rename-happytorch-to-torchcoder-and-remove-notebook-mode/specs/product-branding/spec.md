## ADDED Requirements

### Requirement: TorchCoder is the sole external product name
The project SHALL present `TorchCoder` as the only external product name across repository documentation, the Web interface, deployment assets, and runtime-facing text. The repository MUST NOT expose `HappyTorch` as a current product name in user-visible or operator-visible surfaces.

#### Scenario: User reads the product documentation
- **WHEN** a user reads the repository README or startup instructions
- **THEN** the product is identified as `TorchCoder` rather than `HappyTorch`

#### Scenario: User opens the web application
- **WHEN** a browser loads the main Web page or the server falls back to a plain HTML response
- **THEN** the page title and visible branding identify the product as `TorchCoder`

### Requirement: Deployment-facing identifiers use TorchCoder naming
The project SHALL use `TorchCoder`-aligned names for deployment-facing identifiers that are configured or observed by operators and browsers, including service labels, default database path identifiers, and session cookie naming.

#### Scenario: Operator configures the server runtime
- **WHEN** an operator follows the supported deployment instructions or deployment asset examples
- **THEN** the runtime configuration uses `TorchCoder`-named identifiers instead of `HappyTorch`-named identifiers

#### Scenario: Authenticated browser receives a session
- **WHEN** the Web app creates or clears an authenticated session
- **THEN** the cookie name exposed to the browser uses `TorchCoder` naming rather than `HappyTorch` naming
