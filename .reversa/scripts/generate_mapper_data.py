import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

import os
import json

context_modules_path = "/Users/iagoleal/dev/harness/.reversa/context/modules.json"
out_modules_path = "/Users/iagoleal/dev/harness/.reversa/documentation/assets/data/modules.json"
out_deps_path = "/Users/iagoleal/dev/harness/.reversa/documentation/assets/data/deps.json"

os.makedirs(os.path.dirname(out_modules_path), exist_ok=True)

with open(context_modules_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Vamos extrair submódulos e calcular LOC
mapped_modules = []
submodules_dict = {}

complexity_map = {
    "low": 3,
    "medium": 6,
    "high": 12
}

for mod in data.get("modules", []):
    for sub in mod.get("submodules", []):
        name = sub["name"]
        path = sub["path"]
        comp_str = sub.get("complexity", "medium")
        complexity = complexity_map.get(comp_str, 6)
        
        # Calcular LOC real
        loc = 0
        abs_path = os.path.join("/Users/iagoleal/dev/harness", path)
        if os.path.exists(abs_path):
            if os.path.isdir(abs_path):
                for root, _, files in os.walk(abs_path):
                    for file in files:
                        if file.endswith(".py"):
                            file_p = os.path.join(root, file)
                            try:
                                with open(file_p, "r", encoding="utf-8", errors="ignore") as pf:
                                    loc += len(pf.readlines())
                            except Exception:
                                pass
            elif os.path.isfile(abs_path):
                try:
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as pf:
                        loc = len(pf.readlines())
                except Exception:
                    pass
        
        if loc == 0:
            loc = 50  # fallback
            
        mapped_modules.append({
            "name": name,
            "folder": os.path.dirname(path),
            "loc": loc,
            "complexity": complexity,
            "type": "code"
        })
        submodules_dict[name] = sub

# Gerar dependências
nodes = [{"id": m["name"]} for m in mapped_modules]
edges = []

for m in mapped_modules:
    sub = submodules_dict[m["name"]]
    deps = sub.get("dependencies", [])
    for dep in deps:
        target = None
        dep_clean = dep.split(".")[0] if "." in dep else dep
        if dep_clean == "core":
            target = "domain"
        elif dep_clean in submodules_dict:
            target = dep_clean
            
        if target and target != m["name"]:
            edges.append({
                "from": m["name"],
                "to": target,
                "weight": 1
            })

# Remover duplicados em edges
unique_edges = []
seen_edges = set()
for e in edges:
    key = (e["from"], e["to"])
    if key not in seen_edges:
        seen_edges.add(key)
        unique_edges.append(e)

# Adicionar arestas extras para fechar o grafo de acordo com o dependencies.md
if "adapters" in submodules_dict:
    for target in ["ports", "domain", "bootstrap", "commands"]:
        if target in submodules_dict:
            key = ("adapters", target)
            if key not in seen_edges:
                seen_edges.add(key)
                unique_edges.append({"from": "adapters", "to": target, "weight": 1})

# Mapear ciclos se houver
def find_cycles(nodes_list, edges_list):
    adj = {n["id"]: [] for n in nodes_list}
    for e in edges_list:
        if e["from"] in adj:
            adj[e["from"]].append(e["to"])
            
    visited = {}
    path = []
    detected = []
    
    def dfs(u):
        visited[u] = 1
        path.append(u)
        for v in adj.get(u, []):
            if visited.get(v, 0) == 1:
                idx = path.index(v)
                cycle = path[idx:] + [v]
                detected.append(cycle)
            elif visited.get(v, 0) == 0:
                dfs(v)
        path.pop()
        visited[u] = 2
        
    for n in nodes_list:
        if visited.get(n["id"], 0) == 0:
            dfs(n["id"])
    return detected

cycles_found = find_cycles(nodes, unique_edges)

# Salvar
with open(out_modules_path, "w", encoding="utf-8") as f:
    json.dump(mapped_modules, f, indent=2)

with open(out_deps_path, "w", encoding="utf-8") as f:
    json.dump({
        "nodes": nodes,
        "edges": unique_edges,
        "cycles": cycles_found
    }, f, indent=2)

print(f"Gerado modules.json com {len(mapped_modules)} módulos.")
print(f"Gerado deps.json com {len(unique_edges)} dependências e {len(cycles_found)} ciclos.")
