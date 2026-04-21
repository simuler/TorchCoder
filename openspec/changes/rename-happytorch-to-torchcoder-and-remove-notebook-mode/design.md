## Context

仓库当前处在一个不一致状态：README 顶部已经使用 `TorchCoder`，但 Web 标题、FastAPI 应用名、SQLite 配置名、Cookie 名、systemd 服务说明、Nginx 样例和大量提示文案仍然使用 `HappyTorch`。这种双品牌状态会直接影响用户理解，也会让部署说明和实际运行行为看起来像两个不同产品。

同时，代码库仍保留一整套本地 Jupyter Notebook 练习工作流，包括 `start_jupyter.py`、`prepare_notebooks.py`、Makefile 的 `prepare/jupyter` 入口，以及 `torch_judge/engine.py`、`torch_judge/progress.py` 这类只服务于 Notebook 的辅助接口。但产品已经明显转向账号化 Web 练习，Web 后端也已经直接从 `templates/` 和 `solutions/` 读取题目内容，不依赖本地 `notebooks/` 工作目录。这意味着本地 Notebook 模式已经成为额外维护负担，而不是核心能力。

这次变更是一个跨文档、跨运行时配置、跨 Web/UI 和仓库入口的清理工作。明确设计取舍有必要，否则实现时很容易陷入“保留兼容层”或“顺手重做内容格式”这两种扩大范围的方向。

## Goals / Non-Goals

**Goals:**
- 让仓库和运行时对外只使用 `TorchCoder` 这一产品名。
- 删除本地 Jupyter Notebook 练习工作流及其对应的脚本、入口、文档和辅助代码。
- 在不破坏现有 Web 刷题体验的前提下，尽量缩小仓库维护面。
- 明确新的部署和使用路径是 Web-only。

**Non-Goals:**
- 不在这次变更里把 `templates/` 和 `solutions/` 的内容格式从 `.ipynb` 重写为 Markdown、JSON 或 Python 文件。
- 不改变当前 Web 的账号、题目、提交和持久化模型。
- 不重命名 `torch_judge` 这一内部 Python 包，只处理仍暴露 `HappyTorch` 品牌的代码和配置面。
- 不提供旧 `HappyTorch` 配置名、Cookie 名或启动命令的长期兼容层。

## Decisions

### 1. `TorchCoder` 成为唯一的对外产品标识
实现将统一替换仓库、Web UI、部署样例、运行时提示和默认配置中仍然暴露给用户或运维者的 `HappyTorch` 标识，改为 `TorchCoder`。这包括页面标题、FastAPI 应用标题、静态页面品牌文案、服务说明、反向代理注释、默认数据库文件名、环境变量名和 Session Cookie 名。

Rationale:
- 用户要求是“把代码中所有 HappyTorch 修改为 TorchCoder”，而不是允许继续混用。
- 双品牌会让部署说明、浏览器页面和日志输出缺少可信的一致性。
- 一次性完成替换，比保留历史别名更符合“尽可能精简代码”的目标。

Alternatives considered:
- 保留 `HAPPYTORCH_DB_PATH` 等旧配置名作为兼容别名： rejected，因为会引入额外分支逻辑，并继续把旧品牌暴露在代码和文档里。
- 只修改 UI 文案，不改环境变量、Cookie 和部署资产： rejected，因为运维面仍会保留旧名字，用户仍然会看到混用状态。

### 2. 删除 Notebook 练习工作流，但保留题目 `.ipynb` 资产作为 Web 内容源
本次变更会删除本地 Notebook 启动、准备、进度追踪和 Notebook 判题入口，但不会同步把 `templates/` 和 `solutions/` 的题目资产迁移到新格式。Web 后端已经直接读取这些文件生成题目描述、模板代码和题解，因此保留它们能以最小代价完成“删除 Notebook 模式”这一目标。

Rationale:
- 题目资产与“本地 Notebook 练习方式”不是同一层面的概念；删除用户工作流不必等于重写内容源。
- 直接迁移 70+ 个 `.ipynb` 内容文件会显著扩大范围，也不符合这次变更的核心目标。
- Web 端当前已经不依赖 `prepare_notebooks.py`，说明删除 Notebook 工作流不会阻断线上功能。

Alternatives considered:
- 连同 `templates/`、`solutions/` 一起删除并改成新的内容格式： rejected，因为这是更大的内容建模重构，应另开变更。
- 保留 `start_jupyter.py` 但在 README 里标记为 deprecated： rejected，因为用户明确要求删除这种练习方式。

### 3. 以 Web-only 入口收敛仓库表面
仓库将只保留 Web 启动路径和与 Web 体验直接相关的说明。`start_jupyter.py`、`prepare_notebooks.py`、Makefile 中的 Notebook 相关 target，以及 `torch_judge` 下只被 Notebook 调用的辅助 API 将被删除。README 和部署说明也会同步收敛到 Web-only 模式。

Rationale:
- 当前仓库存在两套练习入口，会增加理解成本和维护面。
- Notebook-only 代码和本地 JSON 进度文件与 Web 账号持久化已经是两套平行系统。
- 删除这部分代码能直接降低未来功能变更时的分支处理成本。

Alternatives considered:
- 保留 notebook 代码仅供开发者内部使用： rejected，因为这仍然意味着需要继续维护第二套入口和文档。
- 仅删除脚本，不删除 `torch_judge` 的 notebook API： rejected，因为会留下无入口但仍可调用的死代码。

### 4. 以显式迁移替代兼容性兜底
这次变更按 breaking cleanup 处理：部署环境变量、Cookie 名和服务资产会直接切换到 `TorchCoder` 命名，已有部署需要手动同步配置。数据库 schema 保持不变，因此现有 SQLite 文件可以通过新环境变量继续复用；但旧 Cookie 会失效，用户需要重新登录。

Rationale:
- 兼容旧命名会扩大实现面，并拖延品牌收敛完成时间。
- 配置和 Cookie 名的变更是可控的运维迁移，风险远低于长期维护双命名。
- 数据模型不变能把 breaking 影响限制在配置和会话层，而不是用户数据层。

Alternatives considered:
- 同时支持旧新两套 env var 和 cookie： rejected，因为与“尽可能精简代码”相冲突。
- 同时重构数据库 schema 以配合新品牌： rejected，因为没有必要，也会增加迁移风险。

## Risks / Trade-offs

- [Risk] 旧部署脚本和环境变量会在升级后失效。 → Mitigation: 在 proposal/spec/tasks 中明确把 env var、service 文件和运行文案更新列为显式迁移步骤。
- [Risk] 更改 Session Cookie 名会让当前登录用户全部掉线。 → Mitigation: 接受一次性重新登录作为可控影响，并在变更说明里标记为 breaking。
- [Risk] 删除 Notebook-only API 可能影响少量仓库外的个人脚本。 → Mitigation: 将这次变更明确定位为 Web-only 收敛，不承诺保留未记录的本地工作流。
- [Risk] 保留 `.ipynb` 作为内容源意味着 Web 端的 notebook 解析代码不会在这次一起消失。 → Mitigation: 把“内容源格式迁移”明确排除在本次范围之外，避免 scope creep。

## Migration Plan

1. 将所有对外可见的 `HappyTorch` 标识切换为 `TorchCoder`。
2. 将默认配置面切换为 `TorchCoder` 命名，例如数据库路径环境变量、Cookie 名和部署资产命名。
3. 删除 Notebook 启动/准备脚本、Makefile 入口和 notebook-only 辅助 API。
4. 更新 README、部署样例和页面文案，使 Web 成为唯一受支持入口。
5. 验证 Web 端题目读取、题解展示、登录、草稿保存和提交评测仍可正常工作。

Rollback strategy:
- 如部署后出现问题，可回滚到上一个提交并恢复旧配置名。
- SQLite 数据文件继续保留原路径内容，因此不会因回滚造成数据迁移损坏。

## Open Questions

- 是否要在本次实现中同步重命名部署资产文件本身，例如 `deploy/happytorch.service` 改为 `deploy/torchcoder.service`？设计倾向于“是”，因为这是外部可见命名的一部分。
- 是否要删除仅服务于本地 Notebook 欢迎页的 `templates/00_welcome.ipynb`？设计倾向于“是”，前提是不影响 Web 题目列表与内容读取。
