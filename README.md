# TorchCoder

**PyTorch 编程练习平台 — 涵盖 LLM、Diffusion、PEFT、RLHF 等方向**

*类似 LeetCode，但专注于张量运算。自托管，专注账号化 Web 刷题体验。即时自动评测，无需 GPU。*

[![PyTorch](https://img.shields.io/badge/PyTorch-ee4c2c?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

![Problems](https://img.shields.io/badge/题目数-36-orange?style=flat-square)
![GPU](https://img.shields.io/badge/GPU-无需-brightgreen?style=flat-square)

> **动态**
> - 2026-03-16：感谢 [damaoooo](https://github.com/damaoooo) 报告题目资产匹配 Bug（attention 与 multihead_attention 冲突）。已将脆弱的后缀匹配替换为显式名称映射，彻底解决此类问题。
> - 2026-03-12：Web 界面侧边栏新增题目分类展示（基础层、注意力机制、RLHF 等），支持折叠/展开，方便按专题刷题。
> - 2026-03-10：感谢 [SongHuang1](https://github.com/SongHuang1) 贡献 MLP XOR 训练题目（纯 NumPy 手写前向+反向传播）。修复 Web 界面问题：class 类题目（LoRA、SwiGLU 等）现已正常工作，执行环境添加 `nn`/`F`/`numpy`/`math` 支持，修复 Windows 上 OpenMP 冲突导致的崩溃，修复 MHA 题解查找，前端增加 60 秒请求超时保护。
> - 2026-03-09：感谢 [chaoyitud](https://github.com/chaoyitud) 新增 ML 与 RLHF 练习题目，感谢 [fiberproduct](https://github.com/fiberproduct) 修复 `torch_judge/tasks/rope.py`。欢迎大家贡献更多题目！
> - 2026-03-06：[浏览器插件](https://github.com/Rivflyyy/happytorch-plugin) 已发布。

---

## 为什么选择 TorchCoder？

如果你正在学习深度学习或准备 ML 面试，你可能遇到过这些问题：

- 看了很多论文，真到写代码时却不知从何下手
- 面试被要求从零实现 `softmax` 或 `MultiHeadAttention`，脑子一片空白
- 想深入理解 Transformer、LoRA、Diffusion、RLHF，但缺乏系统性的动手练习

**TorchCoder** 提供一个友好的实践环境，包含 **36 道精选题目**，从基础激活函数到完整 Transformer 组件和 RLHF 算法，帮助你循序渐进地提升。

| 特性 | 说明 |
|------|------|
| **36 道精选题目** | 从基础到进阶，覆盖主流深度学习技术栈 |
| **自动评测** | 即时反馈，清晰展示每个测试用例的通过/失败状态 |
| **Web 刷题界面** | LeetCode 风格的 Web 界面（Monaco 编辑器） |
| **智能提示** | 卡住时给你思路，而非直接给答案 |
| **参考题解** | 自己尝试后对照学习 |
| **进度追踪** | 记录你的学习旅程 |

---

## 快速开始

### 服务器 Web 部署

```bash
# 1. 创建并激活环境
conda create -n torchcode python=3.11 -y
conda activate torchcode

# 2. 安装依赖
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install numpy
pip install -r web/requirements.txt
pip install -e .

# 3. 配置服务器运行参数
export HOST=0.0.0.0
export PORT=8000
export TORCHCODER_DB_PATH=/srv/torchcoder/data/torchcoder.db
export PUBLIC_ORIGIN=https://simuler.cn
export SESSION_COOKIE_SECURE=true

# 4. 启动 Web 服务
python start_web.py
```

首次排障时可以先访问 `http://<服务器IP>:8000`。当前仓库推荐的公网部署方式，是让 TorchCoder 继续监听 `8000`，再通过 Nginx 对外发布 `https://simuler.cn`。

### 部署说明

- 持久化保存 `TORCHCODER_DB_PATH` 所在目录，确保账号、草稿、做题进度和上次打开题目在服务重启后仍然存在。
- 设置 `PUBLIC_ORIGIN=https://simuler.cn`，让 `start_web.py` 直接打印公网入口，而不是只显示内部监听地址。
- 如果通过 HTTPS 对外提供服务，设置 `SESSION_COOKIE_SECURE=true`，避免登录 Cookie 经由非加密链路发送。
- TorchCoder 内部继续监听 `0.0.0.0:8000`，由 Nginx 接管 `80/443` 对外提供访问。
- 用户登录后会自动恢复上次打开的题目。
- 未登录访客可以看到登录入口，但必须先注册或登录后才能打开题目、查看题解、保存草稿或提交代码。

### Breaking 迁移提醒

- 数据库路径环境变量已从 `HAPPYTORCH_DB_PATH` 改为 `TORCHCODER_DB_PATH`。
- 默认数据库文件名已从 `data/happytorch.db` 改为 `data/torchcoder.db`。
- 会话 Cookie 已从 `happytorch_session` 改为 `torchcoder_session`，升级后现有用户需要重新登录一次。
- 如果你要沿用旧的 SQLite 数据文件，只需把 `TORCHCODER_DB_PATH` 指向原来的数据库路径，例如 `/srv/happytorch/data/happytorch.db`。

### 用 Nginx 绑定 `simuler.cn`

1. 把 `simuler.cn` 的 DNS `A` 记录指向服务器公网 IPv4；如果需要 IPv6，再补充 `AAAA` 记录。
2. 复制并调整仓库内置的 systemd 样例，然后启动 TorchCoder 服务：

```bash
sudo cp deploy/torchcoder.service /etc/systemd/system/torchcoder.service
sudo systemctl daemon-reload
sudo systemctl enable --now torchcoder
```

如果你的部署目录不是 `/srv/torchcoder/app`，请先修改 `deploy/torchcoder.service` 中的 `User`、`Group`、`WorkingDirectory`、`ExecStart` 和 `TORCHCODER_DB_PATH`。

3. 安装 Nginx 和 Certbot，并为 `simuler.cn` 申请证书：

```bash
sudo apt install nginx certbot
sudo certbot certonly --standalone -d simuler.cn
```

4. 启用仓库内置的反向代理样例，并重新加载 Nginx：

```bash
sudo cp deploy/nginx.simuler.cn.conf /etc/nginx/sites-available/simuler.cn.conf
sudo ln -sf /etc/nginx/sites-available/simuler.cn.conf /etc/nginx/sites-enabled/simuler.cn.conf
sudo nginx -t
sudo systemctl reload nginx
```

5. 如果你使用的不是 Let's Encrypt 证书，先修改 `deploy/nginx.simuler.cn.conf` 里的 `ssl_certificate` 和 `ssl_certificate_key` 路径，再重载 Nginx。

仓库内置的 Nginx 样例会把 `http://simuler.cn` 重定向到 `https://simuler.cn`，并将请求代理到 `127.0.0.1:8000`，同时向 TorchCoder 透传 `Host`、`X-Forwarded-Proto` 和 `X-Forwarded-For`。

### 验证清单

- `dig simuler.cn +short` 应返回当前服务器公网 IP。
- `curl -I http://simuler.cn` 应返回跳转到 `https://simuler.cn` 的响应。
- `curl -I https://simuler.cn` 应返回 TorchCoder 的响应，而不是默认 Nginx 欢迎页。
- 浏览器打开 `https://simuler.cn` 时，应能看到 TorchCoder 登录入口或首页。
- 通过 `https://simuler.cn` 注册或登录后，应能拿到会话 Cookie，并正常进入刷题主界面。

---

## Web 模式

类似 LeetCode 的练习界面，功能包括：

- **Monaco 编辑器** — VS Code 同款编辑器，Python 语法高亮
- **随机 / 顺序模式** — 随机抽取未解决的题目，或按顺序刷题
- **即时测试** — 一键运行测试（`Ctrl+Enter`）
- **题解栏目** — 查看参考实现，支持 Markdown 说明和一键复制代码
- **进度面板** — 追踪已通过 / 已尝试 / 待完成状态
- **暗色主题** — 现代化护眼界面

```bash
pip install -r web/requirements.txt
HOST=0.0.0.0 PORT=8000 python start_web.py
# 或：make web HOST=0.0.0.0 PORT=8000 DB_PATH=/srv/torchcoder/data/torchcoder.db
#
# 浏览器打开 http://<服务器IP>:8000
```

Web 端现在要求账号登录后才能开始刷题、查看题解、保存草稿和提交评测。

### Make 快捷命令

```bash
make web HOST=0.0.0.0 PORT=8000 DB_PATH=/srv/torchcoder/data/torchcoder.db
```

### 本地 Web 调试

```bash
HOST=127.0.0.1 PORT=8000 python start_web.py
# 浏览器打开 http://localhost:8000
```

---

## 题目列表（共 36 题）

### 基础层

| # | 题目 | 函数 / 类 | 难度 | 核心概念 |
|:-:|------|----------|:----:|----------|
| 1 | ReLU | `relu(x)` | ![Easy](https://img.shields.io/badge/-简单-4CAF50?style=flat-square) | 激活函数，逐元素操作 |
| 2 | Softmax | `my_softmax(x, dim)` | ![Easy](https://img.shields.io/badge/-简单-4CAF50?style=flat-square) | 数值稳定性，exp/log 技巧 |
| 3 | 线性层 | `SimpleLinear` | ![Medium](https://img.shields.io/badge/-中等-FF9800?style=flat-square) | y = xW^T + b，Kaiming 初始化 |
| 4 | LayerNorm | `my_layer_norm(x, g, b)` | ![Medium](https://img.shields.io/badge/-中等-FF9800?style=flat-square) | 归一化，仿射变换 |
| 7 | BatchNorm | `my_batch_norm(x, g, b)` | ![Medium](https://img.shields.io/badge/-中等-FF9800?style=flat-square) | Batch 与 Layer 统计量，训练/推理行为 |
| 8 | RMSNorm | `rms_norm(x, weight)` | ![Medium](https://img.shields.io/badge/-中等-FF9800?style=flat-square) | LLaMA 风格归一化 |

### 注意力机制

| # | 题目 | 函数 / 类 | 难度 | 核心概念 |
|:-:|------|----------|:----:|----------|
| 5 | 缩放点积注意力 | `scaled_dot_product_attention(Q, K, V)` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | softmax(QK^T/sqrt(d_k))V |
| 6 | 多头注意力 | `MultiHeadAttention` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 并行头，分割/拼接，投影矩阵 |
| 9 | 因果自注意力 | `causal_attention(Q, K, V)` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 自回归掩码，GPT 风格 |
| 10 | 分组查询注意力 | `GroupQueryAttention` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | GQA（LLaMA 2），KV 共享 |
| 11 | 滑动窗口注意力 | `sliding_window_attention(Q, K, V, w)` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | Mistral 风格局部注意力 |
| 12 | 线性注意力 | `linear_attention(Q, K, V)` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 核技巧，O(n*d^2) |

### 完整架构

| # | 题目 | 函数 / 类 | 难度 | 核心概念 |
|:-:|------|----------|:----:|----------|
| 13 | GPT-2 Block | `GPT2Block` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | Pre-norm，因果 MHA + MLP，残差连接 |

### 现代激活函数 *(V2)*

| # | 题目 | 函数 / 类 | 难度 | 核心概念 |
|:-:|------|----------|:----:|----------|
| 14 | GELU | `gelu(x)` | ![Medium](https://img.shields.io/badge/-中等-FF9800?style=flat-square) | 高斯 CDF，erf，BERT/GPT/DiT |
| 15 | SiLU (Swish) | `silu(x)` | ![Easy](https://img.shields.io/badge/-简单-4CAF50?style=flat-square) | x * sigmoid(x)，LLaMA 组件 |
| 16 | SwiGLU | `SwiGLU` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 门控激活，LLaMA MLP |

### 参数高效微调 *(V2)*

| # | 题目 | 函数 / 类 | 难度 | 核心概念 |
|:-:|------|----------|:----:|----------|
| 17 | LoRA | `LoRALinear` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 低秩分解 BA，B 零初始化，alpha/r 缩放 |
| 18 | DoRA | `DoRALinear` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 权重分解，幅度 + 方向 |

### 条件调制 — Diffusion *(V2)*

| # | 题目 | 函数 / 类 | 难度 | 核心概念 |
|:-:|------|----------|:----:|----------|
| 19 | AdaLN | `AdaLN` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 自适应 LayerNorm，DiT 风格 |
| 20 | AdaLN-Zero | `AdaLNZero` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 零初始化门控，稳定训练 |
| 21 | FiLM | `FiLM` | ![Medium](https://img.shields.io/badge/-中等-FF9800?style=flat-square) | 特征级线性调制 |

### LLM 推理组件 *(V2)*

| # | 题目 | 函数 / 类 | 难度 | 核心概念 |
|:-:|------|----------|:----:|----------|
| 22 | RoPE | `apply_rotary_pos_emb(x, pos)` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 旋转位置编码，二维旋转 |
| 23 | KV Cache | `KVCache` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 增量缓存，文本生成加速 |

### 扩散模型训练 *(V2)*

| # | 题目 | 函数 / 类 | 难度 | 核心概念 |
|:-:|------|----------|:----:|----------|
| 24 | Sigmoid 噪声调度 | `sigmoid_schedule(t, ...)` | ![Medium](https://img.shields.io/badge/-中等-FF9800?style=flat-square) | S 曲线噪声调度 |

### ML 基础与解码策略 *(V3 — 社区贡献)*

| # | 题目 | 函数 / 类 | 难度 | 核心概念 |
|:-:|------|----------|:----:|----------|
| 25 | K-Means 聚类 | `kmeans` | ![Medium](https://img.shields.io/badge/-中等-FF9800?style=flat-square) | 迭代质心更新，样本分配 |
| 26 | K 近邻分类 | `knn_predict` | ![Easy](https://img.shields.io/badge/-简单-4CAF50?style=flat-square) | 基于距离的分类 |
| 27 | MLP 反向传播 | `mlp_backward` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 手写两层 MLP 反向传播 |
| 36 | MLP XOR 训练 | `mlp_xor` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 完整 MLP 训练循环（纯 NumPy），He 初始化，MSE 损失 |
| 28 | 贪心解码 | `greedy_decode` | ![Easy](https://img.shields.io/badge/-简单-4CAF50?style=flat-square) | Argmax 逐步选取 token |
| 29 | 束搜索 | `beam_search_decode` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | Beam Search 解码策略 |
| 30 | 温度采样 | `temperature_sample` | ![Medium](https://img.shields.io/badge/-中等-FF9800?style=flat-square) | 温度缩放 softmax 采样 |
| 31 | Top-k 采样 | `top_k_sample` | ![Medium](https://img.shields.io/badge/-中等-FF9800?style=flat-square) | 截断概率分布 |
| 32 | Top-p 采样 | `top_p_sample` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 核采样（Nucleus Sampling） |

### RLHF *(V3 — 社区贡献)*

| # | 题目 | 函数 / 类 | 难度 | 核心概念 |
|:-:|------|----------|:----:|----------|
| 33 | PPO 截断策略损失 | `ppo_clipped_loss` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 截断代理目标函数 |
| 34 | DPO 损失 | `dpo_loss` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 直接偏好优化 |
| 35 | GRPO 损失 | `grpo_loss` | ![Hard](https://img.shields.io/badge/-困难-F44336?style=flat-square) | 群组相对策略优化 |

---

## 使用方法

### Web 练习流程

```
1. 注册 / 登录账号                    →  进入受保护的刷题界面
2. 选择题目                           →  阅读描述、签名和示例
3. 在 Monaco 编辑器中实现代码         →  使用基础 PyTorch / NumPy 运算
4. 点击 Run Tests                     →  查看逐测试用例的即时反馈
5. 自动保存草稿                       →  继续下一次会话
6. 需要时展开题解                     →  对照参考实现学习
```

---

## 建议学习计划

> **总计约 15–20 小时，分 4–5 周完成**

| 周 | 重点 | 题目 | 预计时间 |
|:--:|------|------|:--------:|
| **1** | 基础层 | ReLU、Softmax、Linear、LayerNorm、BatchNorm、RMSNorm | 1–2 小时 |
| **2** | 注意力 | SDPA、MHA、Causal、GQA、Sliding Window、Linear Attention | 3–4 小时 |
| **3** | 现代组件 | GELU、SiLU、SwiGLU、LoRA、DoRA | 2–3 小时 |
| **4** | 进阶话题 | AdaLN、FiLM、RoPE、KV Cache、GPT-2 Block | 3–4 小时 |
| **5** | ML 与 RLHF | K-Means、KNN、MLP 反向传播、MLP XOR 训练、解码策略、PPO、DPO、GRPO | 3–4 小时 |

---

## 添加自定义题目

TorchCoder 使用自动发现机制 — 只需在 `torch_judge/tasks/` 下新增文件：

```python
# torch_judge/tasks/my_task.py
TASK = {
    "title": "我的自定义题目",
    "difficulty": "Medium",       # Easy / Medium / Hard
    "function_name": "my_function",
    "hint": "考虑一下广播机制...",
    "tests": [
        {"name": "基础测试", "code": "assert ..."},
    ]
}
```

无需手动注册，评测引擎会自动发现新题目。然后在 `templates/` 和 `solutions/` 中补充对应题目的仓库内资产，Web 端会直接读取这些文件，无需额外的本地准备步骤。

---

## 常见问题

<details>
<summary><b>需要 GPU 吗？</b></summary>
<br>
不需要。所有题目均在 CPU 上运行，测试的是正确性和理解深度，而非计算吞吐量。
</details>

<details>
<summary><b>如何评测？</b></summary>
<br>
评测引擎使用 <code>torch.allclose</code> 验证数值正确性，通过 autograd 检查梯度是否正确流动，并针对每个操作检测特定的边界情况。
</details>

<details>
<summary><b>进度可以保存吗？</b></summary>
<br>
Web 端会把账号、草稿、做题进度和上次打开的题目保存在 <code>TORCHCODER_DB_PATH</code> 指向的 SQLite 数据库中。如果你沿用旧数据库文件，只需把新的环境变量指向原路径即可。由于会话 Cookie 已从 <code>happytorch_session</code> 改为 <code>torchcoder_session</code>，升级后需要重新登录一次。
</details>

<details>
<summary><b>与 TorchCode 有什么不同？</b></summary>
<br>
TorchCoder 基于 <a href="https://github.com/duoan/TorchCode">TorchCode</a>（13 题）扩展了 23 道新题目，涵盖现代激活函数、LoRA/DoRA、Diffusion 组件、LLM 推理、解码策略、RLHF 算法和纯 NumPy 手写 MLP 训练。
</details>

---

## 致谢

本项目基于 [@duoan](https://github.com/duoan) 的 [TorchCode](https://github.com/duoan/TorchCode)。如果你觉得本项目有帮助，也请给[原项目](https://github.com/duoan/TorchCode)一个 Star。

社区贡献者：
- [chaoyitud](https://github.com/chaoyitud) — ML 基础和 RLHF 练习题目
- [fiberproduct](https://github.com/fiberproduct) — RoPE 题目修复
- [Rivflyyy](https://github.com/Rivflyyy) — [浏览器插件](https://github.com/Rivflyyy/happytorch-plugin)
- [SongHuang1](https://github.com/SongHuang1) — MLP XOR 训练题目
- [damaoooo](https://github.com/damaoooo) — 题目资产匹配 Bug 修复

## 许可证

MIT License — 详见 [LICENSE](LICENSE)。

---

<div align="center">

**如果觉得有用，欢迎点个 Star。**

</div>
