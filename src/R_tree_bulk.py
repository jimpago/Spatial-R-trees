#DIMITRIOS PAGONIS AM: 4985


import sys
import csv

_DIVISORS = [180.0 / 2 ** n for n in range(32)]

def interleave_latlng(lat, lng):
    if not isinstance(lat, float) or not isinstance(lng, float):
        raise ValueError("Supplied arguments must be of type float!")

    if lng > 180:
        x = (lng % 180) + 180.0
    elif lng < -180:
        x = (-((-lng) % 180)) + 180.0
    else:
        x = lng + 180.0

    if lat > 90:
        y = (lat % 90) + 90.0
    elif lat < -90:
        y = (-((-lat) % 90)) + 90.0
    else:
        y = lat + 90.0

    morton_code = ""
    for dx in _DIVISORS:
        digit = 0
        if y >= dx:
            digit |= 2
            y -= dx
        if x >= dx:
            digit |= 1
            x -= dx
        morton_code += str(digit)

    return int(morton_code, 4)

def create_sortedListOfMBRS(file1, file2):
    mbr_list = []
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        while True:
            line1 = next(f1, None)
            line2 = next(f2, None)
            if not line1 or not line2:
                break

            cur_id = line1.split(",")[0]
            start1 = line1.split(",")[1]
            end1 = line1.split(",")[2]
            x_min = float(line2.split(",")[0])
            y_min = float(line2.split(",")[1])
            x_max = float(line2.split(",")[0])
            y_max = float(line2.split(",")[1])

            counter = 0
            for i in range(int(start1), int(end1) + 1):
                cur_x = float(line2.split(",")[0])
                cur_y = float(line2.split(",")[1])

                x_min = min(x_min, cur_x)
                y_min = min(y_min, cur_y)
                x_max = max(x_max, cur_x)
                y_max = max(y_max, cur_y)

                counter += 1
                if counter != ((int(end1) + 1) - int(start1)):
                    line2 = next(f2, None)
                else:
                    x_med = (x_max + x_min) / 2
                    y_med = (y_max + y_min) / 2
                    m_value = interleave_latlng(y_med, x_med)
                    mbr_list.append({
                        "id": cur_id,
                        "mbr": [x_min, x_max, y_min, y_max],
                        "morton_code": m_value
                    })

    mbr_list.sort(key=lambda item: item["morton_code"])
    return mbr_list



id_counter = 0

def build_leaf_nodes(mbr_list, max_cap=20, min_cap=8):
    leaf_nodes = []
    global id_counter

    for i in range(0, len(mbr_list), max_cap):
        smallest_x_min = float('inf')
        smallest_y_min = float('inf')
        largest_x_max = float('-inf')
        largest_y_max = float('-inf')

        for item in mbr_list[i:i + max_cap]:
            x_min, x_max, y_min, y_max = item["mbr"]
            smallest_x_min = min(smallest_x_min, x_min)
            smallest_y_min = min(smallest_y_min, y_min)
            largest_x_max = max(largest_x_max, x_max)
            largest_y_max = max(largest_y_max, y_max)

        leaf = {
            "id": id_counter,
            "mbr": [smallest_x_min, largest_x_max, smallest_y_min, largest_y_max],
            "entries": mbr_list[i:i + max_cap]
        }
        leaf_nodes.append(leaf)
        id_counter += 1

    if len(leaf_nodes) > 1 and len(leaf_nodes[-1]["entries"]) < min_cap:
        last_leaf = leaf_nodes[-1]
        second_last_leaf = leaf_nodes[-2]
        while len(last_leaf["entries"]) < min_cap and len(second_last_leaf["entries"]) > min_cap:
            moved_item = second_last_leaf["entries"].pop()
            last_leaf["entries"].insert(0, moved_item)

    return leaf_nodes

def build_internal_nodes(nodes, max_cap=20, min_cap=8,levels=None):
    
    if levels is None:
        levels = []
    
    levels.insert(0, nodes)

    
    global id_counter
    if len(nodes) == 1:
        return nodes

    parent_nodes = []
    groups = [nodes[i:i + max_cap] for i in range(0, len(nodes), max_cap)]
    if len(groups) > 1 and len(groups[-1]) < min_cap:
        while len(groups[-1]) < min_cap and len(groups[-2]) > min_cap:
            groups[-1].insert(0, groups[-2].pop())

    for group in groups:
        x_min = min(node["mbr"][0] for node in group)
        x_max = max(node["mbr"][1] for node in group)
        y_min = min(node["mbr"][2] for node in group)
        y_max = max(node["mbr"][3] for node in group)
        parent_nodes.append({
            "id": id_counter,
            "mbr": [x_min, x_max, y_min, y_max],
            "children": group
        })
        id_counter += 1

    return build_internal_nodes(parent_nodes, max_cap, min_cap,levels)

def write_rtree_to_file(root):
    with open("Rtree.txt", "w") as output_file:
    # Πρώτα τα φύλλα, μετά οι εσωτερικοί κόμβοι, ρίζα στο τέλος
        for level in reversed(levels):
            for node in level:
                isnonleaf = 1 if "children" in node else 0
                node_id = node["id"]
                entries = []

                if isnonleaf:
                    # Ταξινόμηση των παιδιών κατά id
                    children_sorted = sorted(node["children"], key=lambda c: c["id"])
                    for child in children_sorted:
                        entries.append([child["id"], child["mbr"]])
                else:
                    for entry in node["entries"]:
                        entries.append([entry["id"], entry["mbr"]])

                output_file.write(f"[{isnonleaf}, {node_id}, {entries}]\n")




if len(sys.argv) != 3:
    print("Use the correct number of arguments!")
    sys.exit(1)


file_1 = sys.argv[1] # offsets.txt
file_2 = sys.argv[2] # coords.txt

levels = []
sorted_list = create_sortedListOfMBRS(file_1,file_2)
leaf_nodes = build_leaf_nodes(sorted_list, max_cap=20, min_cap=8)
root = build_internal_nodes(leaf_nodes, max_cap=20, min_cap=8,levels=levels)
write_rtree_to_file(root)
for i, level in enumerate(reversed(levels)):
    num_nodes = len(level)
    label = "node" if num_nodes == 1 else "nodes"
    print(f"{num_nodes} {label} at level {i}")
