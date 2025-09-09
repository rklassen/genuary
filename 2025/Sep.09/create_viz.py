from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import random
import sys
SOURCE_PATTERNS = [
	'wiki_vote_single_root_*.edgelist',
	'wiki_vote_pruned_*x*.edgelist',
	'wiki_vote_ss_*.edgelist',
]


def find_source_path() -> Path:
	# look for the best matching single-source or pruned edgelist file and pick
	# the newest one if multiple candidates exist
	candidates = []
	for pat in SOURCE_PATTERNS:
		candidates.extend(list(Path('.').glob(pat)))

	if not candidates:
		raise SystemExit("No single-source or pruned edgelist file found")

	# sort by modification time and pick newest
	candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
	if len(candidates) > 1:
		print("Multiple candidates found; using the newest:", file=sys.stderr)
		for c in candidates:
			print(" -", c, file=sys.stderr)

	return candidates[0]

def main():
	source_path = find_source_path()

	G = nx.read_edgelist(str(source_path), create_using=nx.DiGraph())

	# Use spring layout for a pleasing force-directed layout; fix seed for
	# reproducibility.
	random.seed(42)
	pos = nx.spring_layout(G, seed=42)

	# Prepare figure at 1920x1080 (dpi=100 -> fig size 19.2 x 10.8 inches)
	dpi = 100
	fig = plt.figure(figsize=(1920 / dpi, 1080 / dpi), dpi=dpi)
	ax = fig.add_subplot(1, 1, 1)
	ax.set_axis_off()

	# Draw edges faintly and nodes small to emphasize structure
	nx.draw_networkx_edges(G, pos, alpha=0.08, edge_color='#333333', width=0.6)
	nx.draw_networkx_nodes(G, pos, node_size=8, node_color='#1f78b4', alpha=0.9)

	# Save PNG with same base filename
	out_path = source_path.with_suffix('.png')
	fig.tight_layout(pad=0)
	fig.savefig(out_path, dpi=dpi, bbox_inches='tight', pad_inches=0)
	plt.close(fig)
	print(f"Wrote image: {out_path}")


if __name__ == '__main__':
	main()
