#!/usr/bin/env python3
"""CMYK Morton dithering with per-channel staggering and a Gabor modulation step.

Pipeline:
1) Downsample by 2x using bilinear filtering.
2) Convert to CMYK.
3) Build a Gabor field per channel and modulate channel intensity.
4) Apply 8x8 Morton threshold dithering per channel with row/channel staggering.
5) Composite channel masks back into a final RGB image.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image


def morton2(x: int, y: int) -> int:
    n = 0
    for bit in range(3):
        n |= ((x >> bit) & 1) << (2 * bit)
        n |= ((y >> bit) & 1) << (2 * bit + 1)
    return n


def build_morton_thresholds_8x8() -> list[list[int]]:
    matrix = [[0] * 8 for _ in range(8)]
    for y in range(8):
        for x in range(8):
            rank = morton2(x, y)
            matrix[y][x] = int((rank + 0.5) * (256.0 / 64.0))
    return matrix


def downsample_half_linear(img: Image.Image) -> Image.Image:
    w, h = img.size
    out_w = max(1, w // 2)
    out_h = max(1, h // 2)
    return img.resize((out_w, out_h), resample=Image.Resampling.BILINEAR)


def gabor_value(
    x: int,
    y: int,
    w: int,
    h: int,
    freq: float,
    sigma: float,
    theta_rad: float,
    phase: float,
) -> float:
    cx = (x + 0.5) - (w * 0.5)
    cy = (y + 0.5) - (h * 0.5)

    xr = cx * math.cos(theta_rad) + cy * math.sin(theta_rad)
    yr = -cx * math.sin(theta_rad) + cy * math.cos(theta_rad)

    gauss = math.exp(-0.5 * (xr * xr + yr * yr) / (sigma * sigma))
    carrier = math.cos(2.0 * math.pi * freq * xr + phase)
    return gauss * carrier


def dither_channel_morton_8x8(
    channel: Image.Image,
    x_phase: int,
    y_phase: int,
    gabor_theta_deg: float,
    gabor_phase_rad: float,
    gabor_strength: float,
    gabor_freq: float,
    gabor_sigma_scale: float,
) -> Image.Image:
    thresholds = build_morton_thresholds_8x8()
    w, h = channel.size
    src = channel.load()

    out = Image.new("L", (w, h), color=0)
    dst = out.load()

    sigma = max(1.0, min(w, h) * gabor_sigma_scale)
    theta_rad = math.radians(gabor_theta_deg)

    for y in range(h):
        py = y + y_phase
        ty = py & 7
        row_offset = 4 if ((py >> 3) & 1) else 0

        for x in range(w):
            tx = (x + x_phase + row_offset) & 7
            v = float(src[x, y])

            g = gabor_value(
                x=x,
                y=y,
                w=w,
                h=h,
                freq=gabor_freq,
                sigma=sigma,
                theta_rad=theta_rad,
                phase=gabor_phase_rad,
            )

            modulated = max(0.0, min(255.0, v + (gabor_strength * 255.0 * g)))
            dst[x, y] = 255 if modulated >= thresholds[ty][tx] else 0

    return out


def process_image(
    input_path: Path,
    output_path: Path,
    gabor_strength: float,
    gabor_freq: float,
    gabor_sigma_scale: float,
) -> None:
    img = Image.open(input_path).convert("RGB")
    half = downsample_half_linear(img)
    cmyk = half.convert("CMYK")
    c, m, y, k = cmyk.split()

    c_d = dither_channel_morton_8x8(
        c,
        x_phase=0,
        y_phase=0,
        gabor_theta_deg=22.5,
        gabor_phase_rad=0.0,
        gabor_strength=gabor_strength,
        gabor_freq=gabor_freq,
        gabor_sigma_scale=gabor_sigma_scale,
    )
    m_d = dither_channel_morton_8x8(
        m,
        x_phase=4,
        y_phase=0,
        gabor_theta_deg=67.5,
        gabor_phase_rad=math.pi / 2.0,
        gabor_strength=gabor_strength,
        gabor_freq=gabor_freq,
        gabor_sigma_scale=gabor_sigma_scale,
    )
    y_d = dither_channel_morton_8x8(
        y,
        x_phase=0,
        y_phase=4,
        gabor_theta_deg=112.5,
        gabor_phase_rad=math.pi,
        gabor_strength=gabor_strength,
        gabor_freq=gabor_freq,
        gabor_sigma_scale=gabor_sigma_scale,
    )
    k_d = dither_channel_morton_8x8(
        k,
        x_phase=4,
        y_phase=4,
        gabor_theta_deg=157.5,
        gabor_phase_rad=3.0 * math.pi / 2.0,
        gabor_strength=gabor_strength,
        gabor_freq=gabor_freq,
        gabor_sigma_scale=gabor_sigma_scale,
    )

    composite = Image.merge("CMYK", (c_d, m_d, y_d, k_d)).convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    composite.save(output_path)
    print(f"Saved: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="2x downsample + CMYK staggered Morton dither + Gabor modulation"
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="Input image(s)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for generated images",
    )
    parser.add_argument(
        "--gabor-strength",
        type=float,
        default=0.18,
        help="Modulation amount; 0 disables Gabor contribution",
    )
    parser.add_argument(
        "--gabor-freq",
        type=float,
        default=0.018,
        help="Cycles per pixel in rotated gabor axis",
    )
    parser.add_argument(
        "--gabor-sigma-scale",
        type=float,
        default=0.45,
        help="Gaussian sigma as fraction of min(image width,height)",
    )
    args = parser.parse_args()

    for input_path in args.inputs:
        out_name = f"{input_path.stem}_half_morton_cmyk_gabor_staggered.png"
        output_path = args.output_dir / out_name
        process_image(
            input_path=input_path,
            output_path=output_path,
            gabor_strength=args.gabor_strength,
            gabor_freq=args.gabor_freq,
            gabor_sigma_scale=args.gabor_sigma_scale,
        )


if __name__ == "__main__":
    main()