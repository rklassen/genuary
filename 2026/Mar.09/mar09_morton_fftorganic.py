#!/usr/bin/env python3
"""Offset-Morton CMYK with per-block FFT shaping before composition.

Pipeline:
1) Downsample input by 2x (bilinear)
2) Offset-Morton threshold each CMYK channel
3) For each 8x8 block/channel: FFT -> band mask -> IFFT
4) Composite continuous CMYK coverage to RGB

Output naming: <subject>-morton-fftorganic.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
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


def rgb_to_gcr_cmyk_channels(rgb_img: Image.Image) -> tuple[Image.Image, Image.Image, Image.Image, Image.Image]:
    """Convert RGB to CMYK with explicit black generation (GCR-style)."""
    rgb = np.array(rgb_img.convert("RGB"), dtype=np.float32) / 255.0

    c = 1.0 - rgb[..., 0]
    m = 1.0 - rgb[..., 1]
    y = 1.0 - rgb[..., 2]

    # Generate K from shared darkness and remove it from chroma inks.
    k = np.minimum(np.minimum(c, m), y)
    c = np.clip(c - k, 0.0, 1.0)
    m = np.clip(m - k, 0.0, 1.0)
    y = np.clip(y - k, 0.0, 1.0)

    c_img = Image.fromarray((c * 255.0).astype(np.uint8), mode="L")
    m_img = Image.fromarray((m * 255.0).astype(np.uint8), mode="L")
    y_img = Image.fromarray((y * 255.0).astype(np.uint8), mode="L")
    k_img = Image.fromarray((k * 255.0).astype(np.uint8), mode="L")
    return c_img, m_img, y_img, k_img


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


def fft_filter_blocks_8x8(
    img_mask: Image.Image,
    low_max: float,
    high_min: float,
    high_max: float,
) -> np.ndarray:
    """Return continuous coverage [0,1] after block FFT filtering.

    Keeps low frequencies and a high band, while removing medium and very-high
    frequencies per 8x8 block.
    """
    arr = (np.array(img_mask.convert("L"), dtype=np.float32) / 255.0)
    h, w = arr.shape
    out = np.zeros_like(arr, dtype=np.float32)

    yy, xx = np.mgrid[0:8, 0:8]
    rr = np.sqrt((yy - 3.5) ** 2 + (xx - 3.5) ** 2)
    keep = (rr <= low_max) | ((rr >= high_min) & (rr <= high_max))

    for y0 in range(0, h, 8):
        for x0 in range(0, w, 8):
            y1 = min(y0 + 8, h)
            x1 = min(x0 + 8, w)
            block = arr[y0:y1, x0:x1]

            pad = np.zeros((8, 8), dtype=np.float32)
            pad[: block.shape[0], : block.shape[1]] = block

            spec = np.fft.fftshift(np.fft.fft2(pad))
            spec *= keep
            recon = np.real(np.fft.ifft2(np.fft.ifftshift(spec)))
            recon = np.clip(recon, 0.0, 1.0)

            out[y0:y1, x0:x1] = recon[: block.shape[0], : block.shape[1]]

    return out


def apply_ink(r: float, g: float, b: float, cov: float, trans: tuple[float, float, float]) -> tuple[float, float, float]:
    r *= 1.0 - cov * (1.0 - trans[0])
    g *= 1.0 - cov * (1.0 - trans[1])
    b *= 1.0 - cov * (1.0 - trans[2])
    return r, g, b


def composite_ink_continuous(
    c_cov: np.ndarray,
    m_cov: np.ndarray,
    y_cov: np.ndarray,
    k_cov: np.ndarray,
) -> Image.Image:
    h, w = c_cov.shape
    out = Image.new("RGB", (w, h))
    dst = out.load()

    paper = (0.965, 0.945, 0.900)
    cyan_t = (0.25, 0.98, 0.98)
    magenta_t = (0.98, 0.30, 0.98)
    yellow_t = (0.98, 0.98, 0.35)
    # Deeper K to avoid muddy midtone blacks in dense shadow regions.
    black_t = (0.08, 0.08, 0.08)

    for y0 in range(h):
        for x0 in range(w):
            r, g, b = paper
            r, g, b = apply_ink(r, g, b, float(c_cov[y0, x0]), cyan_t)
            r, g, b = apply_ink(r, g, b, float(m_cov[y0, x0]), magenta_t)
            r, g, b = apply_ink(r, g, b, float(y_cov[y0, x0]), yellow_t)
            r, g, b = apply_ink(r, g, b, float(k_cov[y0, x0]), black_t)
            dst[x0, y0] = (
                int(max(0, min(255, round(r * 255.0)))),
                int(max(0, min(255, round(g * 255.0)))),
                int(max(0, min(255, round(b * 255.0)))),
            )

    return out


def process_image(
    input_path: Path,
    output_path: Path,
    low_max: float,
    high_min: float,
    high_max: float,
) -> None:
    rgb = Image.open(input_path).convert("RGB")
    half = downsample_half_linear(rgb)
    c, m, y, k = rgb_to_gcr_cmyk_channels(half)

    c_d = dither_channel_morton_8x8(c, x_phase=0, y_phase=0)
    m_d = dither_channel_morton_8x8(m, x_phase=4, y_phase=0)
    y_d = dither_channel_morton_8x8(y, x_phase=0, y_phase=4)
    k_d = dither_channel_morton_8x8(k, x_phase=4, y_phase=4)

    c_cov = fft_filter_blocks_8x8(c_d, low_max=low_max, high_min=high_min, high_max=high_max)
    m_cov = fft_filter_blocks_8x8(m_d, low_max=low_max, high_min=high_min, high_max=high_max)
    y_cov = fft_filter_blocks_8x8(y_d, low_max=low_max, high_min=high_min, high_max=high_max)
    k_cov = fft_filter_blocks_8x8(k_d, low_max=low_max, high_min=high_min, high_max=high_max)
    # Slight K gain after FFT shaping to preserve heavy shadow mass.
    k_cov = np.clip(k_cov * 1.25, 0.0, 1.0)

    rendered = composite_ink_continuous(c_cov, m_cov, y_cov, k_cov)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered.save(output_path)
    print(f"Saved: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offset Morton + per-block FFT shaping before CMYK composition"
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="Input image(s)")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument(
        "--low-max",
        type=float,
        default=1.5,
        help="Keep frequencies with radius <= low-max",
    )
    parser.add_argument(
        "--high-min",
        type=float,
        default=2.6,
        help="Keep high-band frequencies with radius >= high-min",
    )
    parser.add_argument(
        "--high-max",
        type=float,
        default=3.6,
        help="Keep high-band frequencies with radius <= high-max",
    )
    args = parser.parse_args()

    for input_path in args.inputs:
        short = infer_short_name(input_path)
        out_name = f"{short}-morton-fftorganic.png"
        process_image(
            input_path=input_path,
            output_path=args.output_dir / out_name,
            low_max=args.low_max,
            high_min=args.high_min,
            high_max=args.high_max,
        )


if __name__ == "__main__":
    main()
