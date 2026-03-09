"""Compress a file to XZ (.xz) using Python's lzma (XZ) support.

Usage:
	python compress.py [--input PATH] [--output PATH] [--keep]

By default it compresses the file referenced by the `path` variable below.
"""

from __future__ import annotations

import argparse
import lzma
import shutil
from pathlib import Path
import sys

# default path from original file
path = Path(r'/Users/richardklassen/Developer/genuary/2025/Sep.09/Wiki-Vote.txt')


def compress_file(input_path: Path, output_path: Path, keep: bool = False) -> None:
	"""Compress input_path to output_path using XZ (lzma) in streaming mode.

	Writes to a temporary file first and then atomically moves to the final output.
	"""
	if not input_path.exists():
		raise FileNotFoundError(f"Input file not found: {input_path}")

	tmp_output = output_path.with_suffix(output_path.suffix + ".tmp")

	# Use streaming to avoid loading whole file into memory
	with input_path.open('rb') as f_in, lzma.open(tmp_output, 'wb') as f_out:
		shutil.copyfileobj(f_in, f_out)

	# atomically rename
	tmp_output.replace(output_path)

	if not keep:
		try:
			input_path.unlink()
		except Exception:
			# non-fatal: leave original if removal fails
			print(f"Warning: failed to remove original file {input_path}", file=sys.stderr)


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Compress a file to XZ (.xz) using lzma")
	p.add_argument("--input", "-i", type=Path, default=path, help="Input file to compress")
	p.add_argument(
		"--output",
		"-o",
		type=Path,
		help="Output path. If omitted, appends .xz to the input filename",
	)
	p.add_argument(
		"--keep",
		action="store_true",
		help="Keep the original file after successful compression",
	)
	return p.parse_args()


def main() -> int:
	args = parse_args()

	input_path: Path = args.input
	output_path: Path = args.output or input_path.with_suffix(input_path.suffix + ".xz")

	try:
		compress_file(input_path, output_path, keep=args.keep)
	except FileNotFoundError as e:
		print(e, file=sys.stderr)
		return 2
	except Exception as e:
		print(f"Compression failed: {e}", file=sys.stderr)
		return 1

	print(f"Wrote: {output_path}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

