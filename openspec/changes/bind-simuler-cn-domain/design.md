## Context

HappyTorch 当前已经具备公网部署的基础能力：`start_web.py` 默认监听 `0.0.0.0:8000`，`deploy/happytorch.service` 提供了 systemd 示例，README 也提到了可以放在 Nginx/Caddy 后面并通过域名暴露服务。但仓库还没有把“某个具体域名如何成为默认入口”定义成一条受支持、可复用、可验证的部署路径。

这次变更的目标不是重写 Web 应用本身，而是把 `simuler.cn` 接入 HappyTorch 的公网访问链路固定下来。实现会同时影响 DNS/反向代理配置、应用运行时公开源地址、HTTPS Cookie 安全设置，以及中英文部署文档，因此属于跨文档、部署资产和运行时配置的交叉变更。

## Goals / Non-Goals

**Goals:**
- 让 `simuler.cn` 成为 HappyTorch 的默认公网访问入口。
- 明确从域名解析到反向代理再到应用公开地址的完整配置路径。
- 在 HTTPS 域名部署场景下默认使用安全 Cookie 与正确的代理头透传。
- 为运维人员提供可直接落地的部署样例和验证步骤。

**Non-Goals:**
- 不在本次变更中自动管理 DNS 服务商 API 或自动购买域名。
- 不引入新的应用网关、负载均衡器或多节点部署架构。
- 不为多个域名、子域名租户或路径级路由做通用化设计。
- 不改变 HappyTorch 的业务逻辑、鉴权模型或数据库结构。

## Decisions

### 1. 保持 Uvicorn 作为内网应用进程，对外统一由反向代理暴露 `simuler.cn`
HappyTorch 进程继续通过 `HOST=0.0.0.0`、`PORT=8000` 在服务器本机监听，由 Nginx 或等价反向代理接管 `simuler.cn:80/443`，并把请求转发到本地 Web 服务。

Rationale:
- 这与当前 `start_web.py` 和 `deploy/happytorch.service` 的运行方式一致，迁移成本最低。
- 反向代理更适合处理域名绑定、TLS 证书、HTTP 到 HTTPS 跳转和标准代理头。
- 把公网入口与应用进程分离后，后续调试和回滚更简单。

Alternatives considered:
- 直接让 Uvicorn 监听 80/443：拒绝，因为证书管理、权限和重定向处理都会变复杂。
- 将部署方案改为 Caddy 专用：可行，但仓库当前已经更接近 systemd + 显式配置文件方式，Nginx 样例更容易精确表达 `simuler.cn` 的目标接入路径。

### 2. 使用 `PUBLIC_ORIGIN=https://simuler.cn` 作为应用的标准公开地址声明
部署文档和 systemd 样例将显式设置 `PUBLIC_ORIGIN=https://simuler.cn`，使启动提示、文档示例和外部入口保持一致；同时保留 `HOST`/`PORT` 作为内网监听参数。

Rationale:
- 当前仓库已经支持 `PUBLIC_ORIGIN`，但只是作为可选提示，没有纳入默认部署流程。
- 把公开地址显式写入运行时配置，能避免“服务监听地址”和“用户访问地址”混淆。
- 该方式不需要改动业务接口，也不会影响本地调试路径。

Alternatives considered:
- 完全依赖 README 文档文字说明，不设置 `PUBLIC_ORIGIN`：拒绝，因为启动提示仍会显示泛化地址，不利于运维校验。
- 新增专用域名环境变量：拒绝，因为 `PUBLIC_ORIGIN` 已经能表达完整语义，没有必要再扩充配置面。

### 3. 在 HTTPS 域名部署中强制同时配置 TLS、代理头和安全 Cookie
以 `simuler.cn` 对外发布时，反向代理配置必须同时满足三件事：终止 TLS、把 `Host`/`X-Forwarded-*` 头转发给后端、并将 `SESSION_COOKIE_SECURE=true` 纳入受支持配置。

Rationale:
- HappyTorch 已经有基于 Cookie 的认证，HTTPS 场景下不启用安全 Cookie 会留下明显安全缺口。
- 正确代理头是后续日志、绝对地址判断和部署排障的重要基础。
- 将这三个条件作为同一套部署要求，可以避免“域名能打开但登录行为不稳”这类半成功状态。

Alternatives considered:
- 只记录域名绑定，不要求 HTTPS：拒绝，因为当前站点已经支持登录，公网暴露时应以 HTTPS 作为标准路径。
- 只在文档中建议 `SESSION_COOKIE_SECURE`：拒绝，因为该项应成为受支持域名部署的默认要求，而不是可选项。

### 4. 通过仓库内部署资产固化操作步骤，而不是只靠 README 口头描述
实现将补充可直接复用的反向代理配置样例，并更新中英文 README 与 `deploy/happytorch.service`，让部署者能从仓库拿到完整的域名接入参考。

Rationale:
- 当前 README 只提到“可以放到 Nginx/Caddy 后面”，缺少可执行样例。
- 将样例放入 `deploy/` 更便于版本控制和后续维护。
- 域名绑定往往出错在细节，样例文件比说明性文字更可靠。

Alternatives considered:
- 只新增 FAQ 段落：拒绝，因为对域名接入来说，配置片段比问答更有执行价值。
- 只修改 `deploy/happytorch.service`：拒绝，因为 systemd 不能替代反向代理和 TLS 配置本身。

## Risks / Trade-offs

- [Risk] `simuler.cn` 的 DNS 未及时指向服务器公网 IP，导致仓库内配置齐全但域名仍无法访问。 → Mitigation: 在文档和任务中加入 DNS 解析与公网验证步骤。
- [Risk] TLS 证书未签发或续期失败，会导致用户只能访问 HTTP 或看到证书错误。 → Mitigation: 将 HTTP 到 HTTPS 跳转和证书获取/续期检查纳入部署说明。
- [Risk] 代理头透传不完整时，应用日志和调试信息可能仍显示内网地址。 → Mitigation: 在反向代理样例中显式设置 `Host`、`X-Forwarded-Proto` 和 `X-Forwarded-For`。
- [Risk] 在公网 HTTPS 部署中遗漏 `SESSION_COOKIE_SECURE=true` 会降低会话安全性。 → Mitigation: 更新 service 样例和 README，把该变量作为域名部署默认值。
- [Risk] 将域名写死为 `simuler.cn` 会让开源仓库的复用性略受影响。 → Mitigation: 在样例中以 `simuler.cn` 作为当前部署目标，同时保持配置结构易于复制替换。

## Migration Plan

1. 补充反向代理配置样例，定义 `simuler.cn` 到本机 `127.0.0.1:8000` 的转发规则与 HTTPS 行为。
2. 更新 `deploy/happytorch.service`，把 `PUBLIC_ORIGIN=https://simuler.cn` 与 `SESSION_COOKIE_SECURE=true` 纳入受支持示例。
3. 更新 `README.md` 和 `README_CN.md`，补充 `simuler.cn` 的 DNS、证书、代理和验证步骤。
4. 视需要微调 `start_web.py` 的启动提示，使域名部署时输出与 `PUBLIC_ORIGIN` 一致的公网地址。
5. 在服务器上完成 DNS、生效验证、HTTP 跳转和登录流程检查，确认访问 `https://simuler.cn` 时默认进入 HappyTorch。

Rollback strategy:
- 保留应用进程监听 `0.0.0.0:8000` 的方式不变，仅撤回反向代理和文档资产变更即可回到基于 IP 的访问方式。
- 如果 HTTPS 或域名切换失败，可暂时回退为直接访问 `http://<server-ip>:8000`，同时保留原数据库与应用数据不变。

## Open Questions

- 是否只支持根域名 `simuler.cn`，还是需要同时把 `www.simuler.cn` 重定向到根域名？
- 目标服务器当前更适合维护 Nginx 还是 Caddy；如果服务器已装 Caddy，是否仍要以 Nginx 作为仓库内唯一官方样例？
