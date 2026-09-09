"""DDPM forward diffusion process task."""

TASK = {
    "category": "Diffusion",
    "title": "DDPM 前向加噪",
    "difficulty": "Medium",
    "function_name": "ddpm_forward_process",
    "hint": (
        "先在 CPU 上采样每个样本的时间步 t 和标准高斯噪声，再按 beta 线性调度计算 "
        "alpha_bar，并使用 x_t = sqrt(alpha_bar) * x_0 + sqrt(1 - alpha_bar) * noise。"
    ),
    "tests": [
        {
            "name": "返回值形状与 CPU 设备",
            "code": """
import torch
x0 = torch.randn(3, 2, 4)
xt, t, noise = {fn}(x0)
assert xt.shape == x0.shape, f'x_t shape mismatch: {xt.shape}'
assert noise.shape == x0.shape, f'noise shape mismatch: {noise.shape}'
assert t.shape == (x0.shape[0],), f't shape mismatch: {t.shape}'
assert xt.device.type == 'cpu', f'x_t must be on CPU: {xt.device}'
assert t.device.type == 'cpu', f't must be on CPU: {t.device}'
assert noise.device.type == 'cpu', f'noise must be on CPU: {noise.device}'
""",
        },
        {
            "name": "时间步范围与整数类型",
            "code": """
import torch
torch.manual_seed(0)
x0 = torch.zeros(64, 8)
_, t, _ = {fn}(x0)
assert t.dtype == torch.long, f't dtype should be torch.long: {t.dtype}'
assert int(t.min()) >= 0, f't contains a negative timestep: {t.min()}'
assert int(t.max()) < 1000, f't exceeds num_timesteps: {t.max()}'
""",
        },
        {
            "name": "匹配 DDPM 前向公式",
            "code": """
import torch
torch.manual_seed(1234)
x0 = torch.randn(2, 3, 4)
xt, t, noise = {fn}(x0)

torch.manual_seed(1234)
_ = torch.randn(2, 3, 4)  # 与生成输入 x0 消耗同一段 RNG 序列
expected_t = torch.randint(0, 1000, (x0.shape[0],), device='cpu', dtype=torch.long)
expected_noise = torch.randn_like(x0, device='cpu')
betas = torch.linspace(0.0001, 0.02, 1000, device='cpu', dtype=x0.dtype)
alpha_bar = torch.cumprod(1.0 - betas, dim=0)
shape = (x0.shape[0],) + (1,) * (x0.ndim - 1)
expected = (
    alpha_bar.sqrt().gather(0, expected_t).reshape(shape) * x0
    + (1.0 - alpha_bar).sqrt().gather(0, expected_t).reshape(shape) * expected_noise
)
assert torch.equal(t, expected_t), 't should be sampled once from the CPU RNG'
assert torch.allclose(noise, expected_noise), 'noise should be standard Gaussian noise'
assert torch.allclose(xt, expected, atol=1e-6), 'x_t does not match the DDPM formula'
""",
        },
        {
            "name": "支持任意批量与空间维度",
            "code": """
import torch
for shape in [(1, 8), (5, 3, 16, 16), (2, 1, 4, 4, 4)]:
    x0 = torch.randn(*shape)
    xt, t, noise = {fn}(x0)
    assert xt.shape == shape, f'x_t shape mismatch for {shape}: {xt.shape}'
    assert t.shape == (shape[0],), f't shape mismatch for {shape}: {t.shape}'
""",
        },
    ],
}
