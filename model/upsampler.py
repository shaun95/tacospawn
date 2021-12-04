from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class Upsampler(nn.Module):
    """Gaussian upsampler from Non-attentive Tacotron.
    """
    def __init__(self, channels: int, layers: int):
        """Initializer.
        Args:
            channels: size of the input channels.
            layers: the number of the BiGRUs.
        """
        super().__init__()
        self.bigrus = nn.ModuleList([
            nn.GRU(channels * 2, channels, batch_first=True, bidirectional=True)
            for _ in range(layers)])
        self.proj = nn.Linear(channels * 2, 2)

    def forward(self,
                inputs: torch.Tensor,
                mask: torch.Tensor,
                lengths: Optional[torch.Tensor] = None) -> \
            Tuple[torch.Tensor, torch.Tensor, Optional[torch.Tensor]]:
        """Upsampling inputs w.r.t. predicted durations.
        Args:
            inputs: [B, S, C x 2], input tensor.
            mask: [B, S], binary sequence mask.
            lengths: [B], target spectrogram lengths, if provided.
        Returns:
            upsampled: [B, T, C x 2], upsampled feature map.
            lengths: [B], spectrogram lengths.
            factor: [B], residual lengths.
        """
        x = inputs
        for bigru in self.bigrus:
            # [B, S, C x 2]
            x, _ = bigru(x)
        # [B, S, 1], [B, S, 1]
        logdur, range_ = self.proj(x).chunk(2, dim=-1)
        # re-ranging
        if lengths is not None:
            # [B]
            factor = torch.log(lengths) - torch.logsumexp(
                logdur.masked_fill(~mask.to(torch.bool), -np.inf), dim=-1)
            # [B, S]
            logdur = logdur + factor[:, None]
        else:
            factor = None
            # [B]
            lengths = torch.exp(lengths).sum(dim=-1)
        # [B, S], masking
        dur = torch.exp(logdur.squeeze(dim=-1)) * mask
        range_ = F.softplus(range_.squeeze(dim=-1)) * mask
        # [B, S]
        centers = torch.cumsum(dur) - 0.5 * dur
        # [T]
        timesteps = torch.arange(
            lengths.max(), dtype=torch.float32, device=centers.device)
        # [B, T]
        mel_mask = (timesteps[None] < lengths[:, None]).to(torch.float32)
        # [B, T, S]
        attn_mask = mel_mask[..., None] * mask[:, None]
        # [B, T, S]
        align = torch.square(
            (timesteps[None, :, None] - centers[:, None]) / range_[:, None])
        # [B, T, S]
        align = align / (
            (align * mask[:, None]).sum(dim=-1, keepdim=True) + 1e-5)
        # [B, T, S], [B], [B]
        return align * attn_mask, lengths, factor