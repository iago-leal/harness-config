import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

import os
import json
from datetime import datetime

modules_path = "/Users/iagoleal/dev/harness/.reversa/documentation/assets/data/modules.json"
deps_path = "/Users/iagoleal/dev/harness/.reversa/documentation/assets/data/deps.json"
metrics_path = "/Users/iagoleal/dev/harness/.reversa/documentation/assets/data/metrics.json"

with open(modules_path, "r", encoding="utf-8") as f:
    modules = json.load(f)

with open(deps_path, "r", encoding="utf-8") as f:
    deps = json.load(f)

# 1. Agrupar por folder para o treemap
folder_data = {}
for m in modules:
    folder = m["folder"]
    if folder not in folder_data:
        folder_data[folder] = {"loc": 0, "modules": 0}
    folder_data[folder]["loc"] += m["loc"]
    folder_data[folder]["modules"] += 1

treemap_loc_by_folder = []
for folder, info in folder_data.items():
    treemap_loc_by_folder.append({
        "folder": folder,
        "loc": info["loc"],
        "modules": info["modules"]
    })

# 2. Ordenar por complexidade
top_complexity = []
for m in modules:
    top_complexity.append({
        "id": m["name"],
        "complexity": m["complexity"],
        "loc": m["loc"]
    })
top_complexity.sort(key=lambda x: x["complexity"], reverse=True)

# 3. Histograma de LOC
# bins: [0, 50, 100, 200, 500, 1000]
bins = [0, 50, 100, 200, 500, 1000]
counts = [0] * (len(bins) - 1)
for m in modules:
    loc = m["loc"]
    for i in range(len(bins) - 1):
        if bins[i] <= loc < bins[i+1]:
            counts[i] += 1
            break
    else:
        # Se ultrapassar o último bin
        if loc >= bins[-1]:
            counts[-1] += 1

loc_histogram = {
    "bins": bins,
    "counts": counts
}

# 4. Sankey de Dependências
sankey_nodes_set = set()
sankey_links = []
for edge in deps.get("edges", []):
    source = edge["from"]
    target = edge["to"]
    sankey_nodes_set.add(source)
    sankey_nodes_set.add(target)
    sankey_links.append({
        "source": source,
        "target": target,
        "value": edge.get("weight", 1)
    })

dependency_sankey = {
    "nodes": [{"id": n} for n in sankey_nodes_set],
    "links": sankey_links
}

# 5. Distribuição de linguagens
total_loc = sum(m["loc"] for m in modules)
language_distribution = [
    {"language": "Python", "modules": len(modules), "loc": total_loc}
]

metrics = {
    "schemaVersion": 1,
    "generatedAt": datetime.utcnow().isoformat() + "Z",
    "treemap_loc_by_folder": treemap_loc_by_folder,
    "top_complexity": top_complexity,
    "loc_histogram": loc_histogram,
    "dependency_sankey": dependency_sankey,
    "language_distribution": language_distribution
}

with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print("Gerado metrics.json com sucesso.")
