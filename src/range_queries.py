#DIMITRIOS PAGONIS AM: 4985

import sys
import csv


def load_tree_data(R_file):
    leaf_nodes = []
    inner_nodes = []
    root = None
    max_id = -1

    with open(R_file, "r") as f:
        for line in f:
            # Διάβασε τη γραμμή ως λίστα (χρησιμοποιείς eval αν είσαι 100% σίγουρος)
            isnonleaf, node_id, entries = eval(line.strip())

            if node_id > max_id:
                max_id = node_id  # Εντοπισμός ρίζας

            if isnonleaf == 0:
                # Φύλλο — entries: [[object_id, mbr], ...]
                for obj_id, mbr in entries:
                    leaf_nodes.append({
                        "parent_id": node_id,
                        "leaf_id": obj_id,
                        "mbr": mbr
                    })
            else:
                # Εσωτερικός κόμβος — entries: [[child_node_id, mbr], ...]
                inner_nodes.append({
                    "node_id": node_id,
                    "children": entries  # κάθε entry έχει ήδη το MBR
                })
                if node_id == max_id:
                    # Ρίζα — κρατάμε μόνο το ID, το MBR μπορούμε να πάρουμε απ' τα children αν χρειαστεί
                    root = {
                        "root_id": node_id,
                        "children": entries
                    }

    return leaf_nodes, inner_nodes, root

# === Helper Function: Check if two MBRs intersect ===
def mbrs_intersect(a, b):
    return not (a[1] < b[0] or a[0] > b[1] or   # x ranges
                a[3] < b[2] or a[2] > b[3])     # y ranges

# === Build lookup structures ===
def build_lookup_structures(leaf_nodes, inner_nodes, root):
    all_nodes = {node["node_id"]: node for node in inner_nodes}
    all_nodes[root["root_id"]] = root

    leaves_by_parent = {}
    for leaf in leaf_nodes:
        pid = leaf["parent_id"]
        if pid not in leaves_by_parent:
            leaves_by_parent[pid] = []
        leaves_by_parent[pid].append(leaf)

    return all_nodes, leaves_by_parent

# === Recursive range query ===
def range_query(node_id, query_window, all_nodes, leaves_by_parent):
    results = []

    node = all_nodes[node_id]
    children = node["children"]

    for child_id, child_mbr in children:
        if mbrs_intersect(child_mbr, query_window):
            if child_id in leaves_by_parent:
                for leaf in leaves_by_parent[child_id]:
                    if mbrs_intersect(leaf["mbr"], query_window):
                        results.append(leaf["leaf_id"])
            else:
                results.extend(range_query(child_id, query_window, all_nodes, leaves_by_parent))

    return results

# === Process queries from file and print results ===
def process_query_file(query_file_path, root_id, all_nodes, leaves_by_parent):
    with open(query_file_path, "r") as f:
        for line_number, line in enumerate(f):
            parts = list(map(float, line.strip().split()))
            if len(parts) == 4:
                x_low, y_low, x_high, y_high = parts
                window = [x_low, x_high, y_low, y_high]
                ids = range_query(root_id, window, all_nodes, leaves_by_parent)

                # Format the output as required
                result_line = f"{line_number} ({len(ids)}): {','.join(map(str, ids))}"
                print(result_line)  # Print to console


if len(sys.argv) != 3:
    print("Use the correct number of arguments!")
    sys.exit(1)


file_1 = sys.argv[1] # Rtree.txt
file_2 = sys.argv[2] # Rqueries.txt


leaf_nodes, inner_nodes, root = load_tree_data(file_1)
all_nodes, leaves_by_parent = build_lookup_structures(leaf_nodes, inner_nodes, root)
process_query_file(file_2, root["root_id"], all_nodes, leaves_by_parent)
