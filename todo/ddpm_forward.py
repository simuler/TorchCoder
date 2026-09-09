import torch
from typing import Tuple

beta_start = 0.0001
beta_end = 0.02
num_timesteps = 1000


def ddpm_forward_process(
    x_0: torch.Tensor,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Sample a CPU timestep/noise pair and construct the DDPM forward sample."""

    device = torch.device("cpu")
    dtype = x_0.dtype if x_0.is_floating_point() else torch.float32
    x_0 = x_0.to(device=device, dtype=dtype)
    t = torch.randint(
        0,
        num_timesteps,
        (x_0.shape[0],),
        device=device,
        dtype=torch.long,
    )
    noise = torch.randn_like(x_0)

    betas = torch.linspace(
        beta_start,
        beta_end,
        num_timesteps,
        device=device,
        dtype=dtype,
    )
    alphas_cumprod = torch.cumprod(1.0 - betas, dim=0)
    view_shape = (x_0.shape[0],) + (1,) * (x_0.ndim - 1)
    alpha_bar = alphas_cumprod.gather(0, t).reshape(view_shape)

    x_t = alpha_bar.sqrt() * x_0 + (1.0 - alpha_bar).sqrt() * noise
    return x_t, t, noise
