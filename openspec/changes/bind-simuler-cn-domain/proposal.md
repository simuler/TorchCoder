## Why

HappyTorch 已经支持部署到公网服务器，但仓库当前只给出泛化的“可放到 Nginx/Caddy 后面”提示，没有把具体域名接入方案沉淀为受支持的部署能力。现在需要将 `simuler.cn` 绑定到该站点，并让用户访问该域名时默认进入 HappyTorch Web 服务。

## What Changes

- 为 HappyTorch 增加明确的自定义域名接入方案，覆盖 `simuler.cn` 的 DNS、反向代理和应用公开地址配置。
- 补充受支持的 HTTPS 域名部署说明，明确 `PUBLIC_ORIGIN`、`SESSION_COOKIE_SECURE` 与反向代理头的配置关系。
- 新增可直接复用的部署资产示例，使服务器在保留现有 `start_web.py` 与 systemd 启动方式的前提下，对外稳定暴露 `simuler.cn`。
- 更新中英文文档与部署样例，确保运维人员能验证“访问 `https://simuler.cn` 即进入 HappyTorch 站点”。

## Capabilities

### New Capabilities
- `custom-domain-access`: 定义 HappyTorch 通过自定义域名对外提供访问时的 DNS、反向代理、公开源地址和验证要求。
- `https-reverse-proxy-deployment`: 定义 HappyTorch 在 HTTPS 反向代理后的头部透传、Cookie 安全设置和默认入口行为。

### Modified Capabilities

None.

## Impact

- Affected code: `README.md`, `README_CN.md`, `start_web.py`, `deploy/happytorch.service`
- Affected deployment assets: `deploy/` 下新增或更新反向代理配置样例
- Affected runtime configuration: `PUBLIC_ORIGIN`, `HOST`, `PORT`, `SESSION_COOKIE_SECURE`
- Affected systems: DNS 解析、Nginx/Caddy 反向代理、TLS 证书配置、服务器公网访问入口
