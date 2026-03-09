#!/usr/bin/env python3
"""Alternative CMYK dither renderer with flattened output naming.

Style difference from the base script:
- Uses staggered Morton CMYK dithers as masks
- Composites masks with a simple ink-on-paper transmittance model
- Writes compact names: cheetah-morton-offset.png / tenerife-morton-offset.png
"""

from __future__ import annotations

import argparse
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


def infer_short_name(input_path: Path) -> str:
    stem = input_path.stem.lower()
    if "cheetah" in stem:
        return "cheetah"
    if "tenerife" in stem:
        return "tenerife"

    token = "".join(ch if ch.isalnum() else "-" for ch in stem).strip("-")
    return token or "image"


def composite_ink_on_paper(c: Image.Image, m: Image.Image, y: Image.Image, k: Image.Image) -> Image.Image:
    """Composite binary CMYK masks into RGB with a simple transmittance model."""
    w, h = c.size
    cpx = c.load()
    mpx = m.load()
    ypx = y.load()
    kpx = k.load()

    out = Image.new("RGB", (w, h))
    dst = out.load()

    # Off-white paper base.
    paper = (0.965, 0.945, 0.900)

    # Per-ink transmittance (multiplicative) when a dot is present.
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

            dst[x0, y0] = (
                int(max(0, min(255, round(r * 255.0)))),
                int(max(0, min(255, round(g * 255.0)))),
                int(max(0, min(255, round(b * 255.0)))),
            )

    return out


def process_image(input_path: Path, output_path: Path) -> None:
    rgb = Image.open(input_path).convert("RGB")
    half = downsample_half_linear(rgb)
    cmyk = half.convert("CMYK")
    c, m, y, k = cmyk.split()

    c_d = dither_channel_morton_8x8(c, x_phase=0, y_phase=0)
    m_d = dither_channel_morton_8x8(m, x_phase=4, y_phase=0)
    y_d = dither_channel_morton_8x8(y, x_phase=0, y_phase=4)
    k_d = dither_channel_morton_8x8(k, x_phase=4, y_phase=4)

    rendered = composite_ink_on_paper(c_d, m_d, y_d, k_d)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered.save(output_path)
    print(f"Saved: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Alternative CMYK Morton renderer with flattened output naming"
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="Input image(s)")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()

    for input_path in args.inputs:
        short = infer_short_name(input_path)
        out_name = f"{short}-morton-offset.png"
        process_image(input_path, args.output_dir / out_name)


if __name__ == "__main__":
    main()

