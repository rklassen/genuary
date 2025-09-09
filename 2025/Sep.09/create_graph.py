import networkx as nx
import random
import lzma
from pathlib import Path

# 📥 Load the full wiki-Vote graph
# Prefer a compressed input if present. Resolve paths relative to this script so
# the script can be executed from any working directory.
base = Path(__file__).parent
txt_path = base / "Wiki-Vote.txt"
# follow the .txt.xz convention used by the compressor
xz_path = txt_path.with_suffix(txt_path.suffix + ".xz")

if xz_path.exists():
    # open compressed file in text mode and let networkx read from file-like object
    with lzma.open(xz_path, mode="rt") as fh:
        G = nx.read_edgelist(fh, create_using=nx.DiGraph())
else:
    G = nx.read_edgelist(str(txt_path), create_using=nx.DiGraph())

# 🧠 Rank nodes by PageRank to prioritize influential structure
pagerank = nx.pagerank(G)
top_nodes = sorted(pagerank, key=pagerank.get, reverse=True)[:1024]

# 🧱 Induce subgraph from top-ranked nodes
H = G.subgraph(top_nodes).copy()

# ✂️ Trim edges to target count if necessary
if H.number_of_edges() > 7098:
    edges = list(H.edges())
    random.shuffle(edges)
    H.remove_edges_from(edges[7098:])

# 🧪 Pad edges if under target (optional)
elif H.number_of_edges() < 7098:
    candidate_edges = [
        (u, v) for u in top_nodes for v in top_nodes
        if u != v and not H.has_edge(u, v)
    ]
    random.shuffle(candidate_edges)
    H.add_edges_from(candidate_edges[:7098 - H.number_of_edges()])

# ✅ Confirm final structure
print(f"Initial H: {H.number_of_nodes()} nodes, {H.number_of_edges()} edges")

# ---- Prune to largest connected subgraph (weakly connected for directed graphs)
if H.is_directed():
    components = nx.weakly_connected_components(H)
else:
    components = nx.connected_components(H)

# Find the largest component by node count and keep only it
largest_comp = max(components, key=len)
H = H.subgraph(largest_comp).copy()

# ---- Further random culling until target node/edge counts reached
TARGET_NODES = 256
TARGET_EDGES = 1420

if H.number_of_nodes() > TARGET_NODES and H.number_of_edges() > TARGET_EDGES:
    # Randomly remove nodes until either node or edge target is reached
    nodes = list(H.nodes())
    random.shuffle(nodes)

    # remove in batches for speed
    batch_size = max(1, int(len(nodes) * 0.02))
    while H.number_of_nodes() > TARGET_NODES and H.number_of_edges() > TARGET_EDGES and nodes:
        to_drop = [nodes.pop() for _ in range(min(batch_size, len(nodes)))]
        H.remove_nodes_from(to_drop)

    # If still above either target, continue single removals
    while H.number_of_nodes() > TARGET_NODES and H.number_of_edges() > TARGET_EDGES and H.number_of_nodes() > 0:
        n = random.choice(list(H.nodes()))
        H.remove_node(n)

    print(f"After culling: {H.number_of_nodes()} nodes, {H.number_of_edges()} edges")
else:
    print("No culling needed; graph already within target limits")

# ---- Create single source: pick existing node that reaches all, else add a new root
# Score nodes by connectivity
deg = {n: H.out_degree(n) + H.in_degree(n) for n in H.nodes()}
top16 = sorted(deg, key=deg.get, reverse=True)[:16]

# If any top node can reach all others, choose it as root
total_nodes = set(H.nodes())
selected_root = None
for candidate in top16:
    reachable = set(nx.descendants(H, candidate)) | {candidate}
    if reachable >= total_nodes:
        selected_root = candidate
        print(f"Selected existing node {candidate} as root; reaches all nodes")
        break

edges_added = []
if selected_root is None:
    # create unique root
    new_root = "_ROOT_"
    i = 0
    while new_root in H:
        i += 1
        new_root = f"_ROOT_{i}"
    H.add_node(new_root)
    # Greedy set cover: precompute reach sets for candidates then iteratively
    # select the node that covers the largest number of yet-uncovered nodes.
    universe = set(H.nodes()) - {new_root}
    reach = {n: (set(nx.descendants(H, n)) | {n}) & universe for n in universe}

    covered = set()
    candidates = set(universe)

    while covered != universe and candidates:
        # pick candidate with largest uncovered reach
        best_node = max(candidates, key=lambda n: len(reach[n] - covered))
        gain = len(reach[best_node] - covered)
        if gain == 0:
            # no candidate gives new coverage; remaining nodes are isolated
            break

        H.add_edge(new_root, best_node)
        edges_added.append((new_root, best_node))
        covered |= reach[best_node]
        candidates.remove(best_node)

    # Any nodes still not covered must be directly connected
    missing = universe - covered
    for m in missing:
        H.add_edge(new_root, m)
        edges_added.append((new_root, m))

    selected_root = new_root

# Remove nodes not reachable from selected_root
reachable = set(nx.descendants(H, selected_root)) | {selected_root}
to_remove = [n for n in H.nodes() if n not in reachable]
if to_remove:
    H.remove_nodes_from(to_remove)

# Save a single final edgelist with counts
final_nn = H.number_of_nodes()
final_ee = H.number_of_edges()
final_name = f"wiki_vote_ss_{final_nn}x{final_ee}.edgelist"
nx.write_edgelist(H, final_name, data=False)
print(f"Saved final single-source graph: {final_name} ({final_nn} nodes, {final_ee} edges); removed {len(to_remove)} unreachable nodes")