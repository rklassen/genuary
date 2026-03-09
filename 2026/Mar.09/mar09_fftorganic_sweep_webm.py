#!/usr/bin/env python3
"""Animate linear FFT-option progression and encode WebM."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from mar09_morton_fftorganic import infer_short_name, process_image


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render WebM animations with linear progression of FFT options"
    )
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--frames", type=int, default=24)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--low-start", type=float, default=1.2)
    parser.add_argument("--low-end", type=float, default=2.4)
    parser.add_argument("--high-min-start", type=float, default=3.8)
    parser.add_argument("--high-min-end", type=float, default=2.0)
    parser.add_argument("--high-max-start", type=float, default=4.6)
    parser.add_argument("--high-max-end", type=float, default=3.1)
    parser.add_argument("--keep-frames", action="store_true")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for input_path in args.inputs:
        short = infer_short_name(input_path)
        frame_dir = args.output_dir / f"_frames_{short}"
        frame_dir.mkdir(parents=True, exist_ok=True)

        frame_count = max(2, args.frames)
        for i in range(frame_count):
            t = i / float(frame_count - 1)
            low = lerp(args.low_start, args.low_end, t)
            high_min = lerp(args.high_min_start, args.high_min_end, t)
            high_max = lerp(args.high_max_start, args.high_max_end, t)

            frame_path = frame_dir / f"frame_{i:04d}.png"
            process_image(
                input_path=input_path,
                output_path=frame_path,
                low_max=low,
                high_min=high_min,
                high_max=high_max,
            )

        webm_path = args.output_dir / f"{short}-morton-fftorganic-sweep.webm"
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-framerate",
            str(args.fps),
            "-i",
            str(frame_dir / "frame_%04d.png"),
            "-c:v",
            "libvpx-vp9",
            "-pix_fmt",
            "yuv420p",
            "-b:v",
            "0",
            "-crf",
            "32",
            str(webm_path),
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Saved: {webm_path}")

        if not args.keep_frames:
            shutil.rmtree(frame_dir)


if __name__ == "__main__":
    main()
