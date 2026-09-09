"""Web UI localization helpers."""

from __future__ import annotations

from typing import Any

DIFFICULTY_LABELS = {
    "Easy": "简单",
    "Medium": "中等",
    "Hard": "困难",
}

CATEGORY_LABELS = {
    "基础层": "基础层",
    "注意力机制": "注意力机制",
    "完整架构": "完整架构",
    "现代激活函数": "现代激活函数",
    "参数高效微调": "参数高效微调",
    "条件调制 — Diffusion": "条件调制 — 扩散模型",
    "LLM 推理组件": "LLM 推理组件",
    "Diffusion": "扩散模型（Diffusion）",
    "扩散模型训练": "扩散模型训练",
    "ML 基础与解码策略": "机器学习基础与解码策略",
    "RLHF": "RLHF",
}

TASK_LOCALIZATION = {
    "relu": {
        "title": "实现 ReLU",
        "hint": "逐元素与 0 比较并取较大值即可，避免直接调用现成的激活函数实现。",
    },
    "softmax": {
        "title": "实现 Softmax",
        "hint": "先减去最大值再做指数和归一化，保证数值稳定性。",
    },
    "batchnorm": {
        "title": "实现 BatchNorm",
        "hint": "沿批次维度计算每个特征的均值和方差，再做归一化与仿射变换；方差使用 unbiased=False。",
    },
    "layernorm": {
        "title": "实现 LayerNorm",
        "hint": "沿最后一个维度计算均值和方差，然后乘以 gamma、加上 beta。",
    },
    "linear": {
        "title": "简易线性层",
        "hint": "核心公式是 y = x @ W^T + b，权重初始化可按 1/sqrt(in_features) 缩放。",
    },
    "rmsnorm": {
        "title": "实现 RMSNorm",
        "hint": "只基于均方根做归一化，不需要减均值，最后再乘以可学习权重。",
    },
    "attention": {
        "title": "Softmax 注意力",
        "hint": "先计算 QK^T / sqrt(d_k)，再对最后一维做 softmax，最后与 V 相乘。",
    },
    "causal_attention": {
        "title": "因果自注意力",
        "hint": "与普通注意力相同，但要用上三角掩码屏蔽未来位置，再执行 softmax。",
    },
    "gqa": {
        "title": "分组查询注意力",
        "hint": "Q 头数多于 KV 头数时，需要把 KV 头按组扩展到与 Q 对齐。",
    },
    "linear_attention": {
        "title": "线性自注意力",
        "hint": "把 softmax 注意力改写成特征映射形式，先算 phi(K)^T @ V，再与 phi(Q) 相乘并做归一化。",
    },
    "mha": {
        "title": "多头注意力",
        "hint": "先做线性投影，再拆分多头、分别计算注意力、最后拼回并经过输出投影。",
    },
    "sliding_window": {
        "title": "滑动窗口注意力",
        "hint": "每个位置只允许关注窗口范围内的 token，其余位置用负无穷掩码屏蔽。",
    },
    "gpt2_block": {
        "title": "GPT-2 Transformer 模块",
        "hint": "采用 pre-norm 结构：残差连接包住因果注意力和 MLP 两个子层。",
    },
    "silu": {
        "title": "SiLU（Swish）激活",
        "hint": "公式是 x * sigmoid(x)，实现时保持逐元素计算即可。",
    },
    "gelu": {
        "title": "GELU 激活",
        "hint": "可以按高斯分布 CDF 的精确定义实现，也可以使用常见的 tanh 近似式。",
    },
    "swiglu": {
        "title": "SwiGLU 激活",
        "hint": "先分别得到 gate 和 up 两个投影，再计算 Swish(gate) * up。",
    },
    "dora": {
        "title": "DoRA 线性层",
        "hint": "把权重拆成幅值和方向，LoRA 只更新方向部分，最后重新归一化后乘回幅值。",
    },
    "lora": {
        "title": "LoRA 线性层",
        "hint": "低秩更新写成 BA，并按 alpha/r 缩放；常见做法是 A 随机初始化、B 零初始化。",
    },
    "film": {
        "title": "FiLM 层",
        "hint": "根据条件向量预测缩放与偏移参数，对输入做逐特征仿射调制。",
    },
    "adaln": {
        "title": "AdaLN（自适应 LayerNorm）",
        "hint": "先做 LayerNorm，再根据条件向量预测 gamma 和 beta，对归一化结果做调制。",
    },
    "adaln_zero": {
        "title": "AdaLN-Zero",
        "hint": "最后一层和残差门控都以 0 初始化，让调制能力从零开始逐步学习。",
    },
    "kv_cache": {
        "title": "注意力 KV 缓存",
        "hint": "缓存历史 K、V 张量，支持增量追加，并能高效返回当前完整缓存。",
    },
    "rope": {
        "title": "旋转位置编码（RoPE）",
        "hint": "把相邻两个通道视作二维向量，按位置相关角度做旋转变换。",
    },
    "snr": {
        "title": "Sigmoid 噪声调度",
        "hint": "利用 sigmoid 的 S 曲线把时间步映射到平滑变化的噪声强度区间。",
    },
    "greedy_sampling": {
        "title": "贪心搜索解码",
        "hint": "每一步都直接选择当前 logits 最大的 token，本质上就是 argmax。",
    },
    "knn": {
        "title": "K 近邻分类",
        "hint": "先计算样本与训练集距离，再取最近的 k 个邻居做多数投票。",
    },
    "kmeans": {
        "title": "K-Means 聚类",
        "hint": "在“分配样本到最近质心”和“用簇内样本更新质心”之间反复迭代。",
    },
    "temperature_sampling": {
        "title": "温度采样",
        "hint": "先用温度对 logits 做缩放，再对 softmax 分布进行随机采样。",
    },
    "top_k_sampling": {
        "title": "Top-k 采样",
        "hint": "只保留概率最高的 k 个候选，其余位置屏蔽后再归一化采样。",
    },
    "beam_search": {
        "title": "Beam Search 解码",
        "hint": "维护多个最高分候选序列，每一步扩展后保留总分最优的若干条路径。",
    },
    "mlp_backward": {
        "title": "两层 MLP 手写反向传播",
        "hint": "按链式法则依次求出输出层和隐藏层对权重、偏置以及输入的梯度。",
    },
    "mlp_xor": {
        "title": "手写 NumPy 训练 XOR 两层 MLP",
        "hint": "完整实现前向、反向和参数更新流程，让网络能够拟合 XOR 数据。",
    },
    "top_p_sampling": {
        "title": "Top-p 采样",
        "hint": "按概率从高到低累加，保留累计概率首次超过 p 的最小候选集合后再采样。",
    },
    "dpo_loss": {
        "title": "DPO 损失",
        "hint": "比较优选与劣选样本相对参考策略的对数概率差，再经过 sigmoid 形式构造损失。",
    },
    "grpo_loss": {
        "title": "GRPO 损失",
        "hint": "以组内相对优势为核心，对策略比值做裁剪并聚合同组样本的更新信号。",
    },
    "ppo_loss": {
        "title": "PPO 截断策略损失",
        "hint": "计算新旧策略概率比值，并与裁剪后的目标取较小值以稳定训练。",
    },
}


def localize_task(task_id: str, task: dict[str, Any]) -> dict[str, str]:
    localized = TASK_LOCALIZATION.get(task_id, {})
    function_name = task.get("function_name", "")
    title = localized.get("title", task.get("title", ""))
    hint = localized.get("hint", task.get("hint", ""))
    difficulty = DIFFICULTY_LABELS.get(task.get("difficulty", ""), task.get("difficulty", ""))
    category = CATEGORY_LABELS.get(task.get("category", ""), task.get("category", ""))
    target = "类" if function_name[:1].isupper() else "函数"

    description = (
        f"请实现 **{title}**。\n\n"
        f"你需要补全{target} `{function_name}`，使其通过平台中的全部测试用例。\n\n"
        "### 关键提示\n"
        f"- {hint}\n"
    )

    solution_markdown = (
        f"# 参考题解：{title}\n\n"
        "下方给出该题的参考实现代码，可结合代码与测试结果对照理解。\n\n"
        "### 核心思路\n"
        f"- {hint}\n"
    )

    return {
        "title": title,
        "hint": hint,
        "difficulty_label": difficulty,
        "category_label": category,
        "description": description,
        "solution_markdown": solution_markdown,
    }
