## 1. Reverse Proxy Entrypoint

- [x] 1.1 Add a reverse-proxy deployment sample under `deploy/` for `simuler.cn` that forwards traffic to the local HappyTorch service on `127.0.0.1:8000`.
- [x] 1.2 Configure the sample proxy to redirect `http://simuler.cn` to `https://simuler.cn` and document the expected TLS certificate path or issuance flow.
- [x] 1.3 Include the required forwarded headers (`Host`, `X-Forwarded-Proto`, `X-Forwarded-For`) in the supported proxy configuration.

## 2. Application Runtime Alignment

- [x] 2.1 Update `deploy/happytorch.service` so the supported domain deployment example sets `PUBLIC_ORIGIN=https://simuler.cn`.
- [x] 2.2 Update `deploy/happytorch.service` and related guidance so HTTPS domain deployment uses `SESSION_COOKIE_SECURE=true`.
- [x] 2.3 Review `start_web.py` startup output and adjust it if needed so the public access hint stays consistent with the configured `PUBLIC_ORIGIN`.

## 3. Documentation

- [x] 3.1 Update `README.md` with a deployment walkthrough for `simuler.cn`, including DNS mapping, reverse-proxy setup, HTTPS enablement, and post-deploy verification.
- [x] 3.2 Update `README_CN.md` with the same `simuler.cn` deployment walkthrough and runtime configuration details.
- [x] 3.3 Document the validation checklist for accessing HappyTorch through `https://simuler.cn`, including DNS resolution, HTTP-to-HTTPS redirect, homepage load, and login flow checks.

## 4. Verification

- [x] 4.1 Verify the final deployment assets are internally consistent across `deploy/`, `README.md`, `README_CN.md`, and `start_web.py`.
- [ ] 4.2 Validate on the target server that visiting `https://simuler.cn` reaches the HappyTorch site and that direct HTTP access redirects to HTTPS.
- [ ] 4.3 Confirm authenticated usage still works over the domain entrypoint, including login, session cookie behavior, and loading the main web UI.
