#!/usr/bin/env python3
"""Offset-Morton CMYK + continuous Gabor uncertainty blend.

Pipeline:
1) Downsample input by 2x (bilinear)
2) Build base image using offset Morton dithering (no gabor)
3) Build continuous CMYK uncertainty image using Gabor perturbation
4) Average base and uncertainty composites

Output naming: <subject>-morton-uncertainty.png
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
            matrix[y][x] = int((rank + 0.5) * 4.0)
    return matrix


def downsample_half_linear(img: Image.Image) -> Image.Image:
    w, h = img.size
    return img.resize((max(1, w // 2), max(1, h // 2)), resample=Image.Resampling.BILINEAR)


def infer_short_name(input_path: Path) -> str:
    stem = input_path.stem.lower()
    if "cheetah" in stem:
        return "cheetah"
    if "tenerife" in stem:
        return "tenerife"
    token = "".join(ch if ch.isalnum() else "-" for ch in stem).strip("-")
    return token or "image"


def dither_channel_morton_8x8(channel: Image.Image, x_phase: int, y_phase: int) -> Image.Image:
    thresholds = build_morton_thresholds_8x8()
    w, h = channel.size
    src = channel.load()

    out = Image.new("1", (w, h))
    dst = out.load()

    for y in range(h):
        py = y + y_phase
        ty = py & 7
        row_offset = 4 if ((py >> 3) & 1) else 0
        for x in range(w):
            tx = (x + x_phase + row_offset) & 7
            dst[x, y] = 255 if src[x, y] >= thresholds[ty][tx] else 0

    return out


def gabor_value(x: int, y: int, w: int, h: int, freq: float, sigma: float, theta_rad: float, phase: float) -> float:
    cx = (x + 0.5) - (w * 0.5)
    cy = (y + 0.5) - (h * 0.5)

    xr = cx * math.cos(theta_rad) + cy * math.sin(theta_rad)
    yr = -cx * math.sin(theta_rad) + cy * math.cos(theta_rad)

    gauss = math.exp(-0.5 * (xr * xr + yr * yr) / (sigma * sigma))
    carrier = math.cos(2.0 * math.pi * freq * xr + phase)
    return gauss * carrier


def channel_uncertainty_coverage(
    channel: Image.Image,
    theta_deg: float,
    phase_rad: float,
    strength: float,
    freq: float,
    sigma_scale: float,
) -> list[list[float]]:
    w, h = channel.size
    src = channel.load()

    sigma = max(1.0, min(w, h) * sigma_scale)
    theta = math.radians(theta_deg)

    cov = [[0.0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            base = src[x, y] / 255.0
            g = gabor_value(x, y, w, h, freq=freq, sigma=sigma, theta_rad=theta, phase=phase_rad)

            # Larger uncertainty in mid-tones; low in extremes.
            tone_weight = 0.2 + 3.2 * (base * (1.0 - base))
            v = base + (strength * g * tone_weight)
            cov[y][x] = max(0.0, min(1.0, v))

    return cov


def composite_ink_binary(c: Image.Image, m: Image.Image, y: Image.Image, k: Image.Image) -> Image.Image:
    w, h = c.size
    cpx = c.load()
    mpx = m.load()
    ypx = y.load()
    kpx = k.load()

    out = Image.new("RGB", (w, h))
    dst = out.load()

    paper = (0.965, 0.945, 0.900)
    cyan_t = (0.25, 0.98, 0.98)
    magenta_t = (0.98, 0.30, 0.98)
    yellow_t = (0.98, 0.98, 0.35)
    black_t = (0.30, 0.30, 0.30)

    for y0 in range(h):
        for x0 in range(w):
            r, g, b = paper

            if cpx[x0, y0] != 0:
                r *= cyan_t[0]
                g *= cyan_t[1]
                b *= cyan_t[2]
            if mpx[x0, y0] != 0:
                r *= magenta_t[0]
                g *= magenta_t[1]
                b *= magenta_t[2]
            if ypx[x0, y0] != 0:
                r *= yellow_t[0]
                g *= yellow_t[1]
                b *= yellow_t[2]
            if kpx[x0, y0] != 0:
                r *= black_t[0]
                g *= black_t[1]
                b *= black_t[2]

            dst[x0, y0] = (int(r * 255.0), int(g * 255.0), int(b * 255.0))

    return out


def apply_ink(r: float, g: float, b: float, cov: float, trans: tuple[float, float, float]) -> tuple[float, float, float]:
    # Continuous coverage interpolation from no-ink (1.0) to full ink transmittance.
    r *= 1.0 - cov * (1.0 - trans[0])
    g *= 1.0 - cov * (1.0 - trans[1])
    b *= 1.0 - cov * (1.0 - trans[2])
    return r, g, b


def composite_ink_continuous(
    c_cov: list[list[float]],
    m_cov: list[list[float]],
    y_cov: list[list[float]],
    k_cov: list[list[float]],
) -> Image.Image:
    h = len(c_cov)
    w = len(c_cov[0]) if h else 0

    out = Image.new("RGB", (w, h))
    dst = out.load()

    paper = (0.965, 0.945, 0.900)
    cyan_t = (0.25, 0.98, 0.98)
    magenta_t = (0.98, 0.30, 0.98)
    yellow_t = (0.98, 0.98, 0.35)
    black_t = (0.30, 0.30, 0.30)

    for y0 in range(h):
        for x0 in range(w):
            r, g, b = paper

            r, g, b = apply_ink(r, g, b, c_cov[y0][x0], cyan_t)
            r, g, b = apply_ink(r, g, b, m_cov[y0][x0], magenta_t)
            r, g, b = apply_ink(r, g, b, y_cov[y0][x0], yellow_t)
            r, g, b = apply_ink(r, g, b, k_cov[y0][x0], black_t)

            dst[x0, y0] = (
                int(max(0, min(255, round(r * 255.0)))),
                int(max(0, min(255, round(g * 255.0)))),
                int(max(0, min(255, round(b * 255.0)))),
            )

    return out


def process_image(
    input_path: Path,
    output_path: Path,
    blend: float,
    uncertainty_strength: float,
    gabor_freq: float,
    gabor_sigma_scale: float,
) -> None:
    rgb = Image.open(input_path).convert("RGB")
    half = downsample_half_linear(rgb)
    cmyk = half.convert("CMYK")
    c, m, y, k = cmyk.split()

    # Base: offset Morton (no gabor).
    c_d = dither_channel_morton_8x8(c, x_phase=0, y_phase=0)
    m_d = dither_channel_morton_8x8(m, x_phase=4, y_phase=0)
    y_d = dither_channel_morton_8x8(y, x_phase=0, y_phase=4)
    k_d = dither_channel_morton_8x8(k, x_phase=4, y_phase=4)
    base = composite_ink_binary(c_d, m_d, y_d, k_d)

    # Continuous gabor uncertainty composite.
    c_cov = channel_uncertainty_coverage(c, 22.5, 0.0, uncertainty_strength, gabor_freq, gabor_sigma_scale)
    m_cov = channel_uncertainty_coverage(m, 67.5, math.pi / 2.0, uncertainty_strength, gabor_freq, gabor_sigma_scale)
    y_cov = channel_uncertainty_coverage(y, 112.5, math.pi, uncertainty_strength, gabor_freq, gabor_sigma_scale)
    k_cov = channel_uncertainty_coverage(k, 157.5, 3.0 * math.pi / 2.0, uncertainty_strength, gabor_freq, gabor_sigma_scale)
    uncertain = composite_ink_continuous(c_cov, m_cov, y_cov, k_cov)

    result = Image.blend(base, uncertain, blend)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)
    print(f"Saved: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offset Morton base + continuous Gabor uncertainty average"
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="Input image(s)")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--blend", type=float, default=1.0, help="0=base only, 1=uncertainty only")
    parser.add_argument("--uncertainty-strength", type=float, default=0.22)
    parser.add_argument("--gabor-freq", type=float, default=0.018)
    parser.add_argument("--gabor-sigma-scale", type=float, default=0.03125)
    args = parser.parse_args()

    blend = max(0.0, min(1.0, args.blend))

    for input_path in args.inputs:
        short = infer_short_name(input_path)
        out_name = f"{short}-morton-uncertainty.png"
        process_image(
            input_path=input_path,
            output_path=args.output_dir / out_name,
            blend=blend,
            uncertainty_strength=args.uncertainty_strength,
            gabor_freq=args.gabor_freq,
            gabor_sigma_scale=args.gabor_sigma_scale,
        )


if __name__ == "__main__":
    main()

