## Why

仓库当前同时混用 `HappyTorch` 与 `TorchCoder` 两套命名，导致 README、Web 标题、部署资产和运行时文案对外呈现不一致。与此同时，项目已经明显转向账号化的 Web 刷题体验，但仍保留本地 Jupyter Notebook 工作流及其配套脚本、文档和判题接口，增加了维护成本，也让仓库边界变得模糊。

## What Changes

- 将仓库、Web 界面、部署资产和运行时文案中对外暴露的产品名统一为 `TorchCoder`。
- 清理仍以 `HappyTorch` 命名的服务说明、页面标题、提示信息和部署示例，避免用户在安装、访问和运维时看到混杂品牌。
- **BREAKING**: 删除本地 Jupyter Notebook 练习方式，不再提供 Notebook 启动脚本、准备脚本、Makefile 入口和相关文档。
- **BREAKING**: 删除只服务于本地 Notebook 工作流的判题/进度辅助代码，尽可能将仓库收敛到 Web 练习所需的最小实现面。
- 保留 Web 刷题、账号登录、题目读取、题解展示和自动评测能力，确保收敛后仍能完整支撑当前在线使用场景。

## Capabilities

### New Capabilities
- `product-branding`: 定义仓库和运行时所有对外暴露标识必须统一使用 `TorchCoder`，不再混用 `HappyTorch`。
- `web-only-practice`: 定义受支持的练习入口仅为 Web 应用，仓库不得继续暴露本地 Jupyter Notebook 练习工作流。

### Modified Capabilities

None.

## Impact

- Affected code: `README.md`, `Makefile`, `start_web.py`, `start_jupyter.py`, `prepare_notebooks.py`, `torch_judge/__init__.py`, `torch_judge/engine.py`, `torch_judge/progress.py`, `web/app.py`, `web/persistence.py`, `web/__init__.py`, `web/static/index.html`, `web/static/app.js`
- Affected content/assets: `deploy/happytorch.service`, `deploy/nginx.simuler.cn.conf`, `templates/`, `solutions/`
- Affected behavior: product naming, supported local entrypoints, repository surface area, Web-only practice positioning
- Affected users: existing Notebook-mode users must migrate to the Web interface
