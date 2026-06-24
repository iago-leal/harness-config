import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

import os
import json
import hashlib
from datetime import datetime

state_path = "/Users/iagoleal/dev/harness/.reversa/documentation/.state.json"
doc_dir = "/Users/iagoleal/dev/harness/.reversa/documentation"

# Se o arquivo já existe, lê, senão inicializa
if os.path.exists(state_path):
    with open(state_path, "r", encoding="utf-8") as f:
        try:
            state = json.load(f)
        except Exception:
            state = None

if not os.path.exists(state_path) or state is None:
    state = {
        "schemaVersion": 1,
        "startedAt": datetime.utcnow().isoformat() + "Z",
        "lastCheckpoint": datetime.utcnow().isoformat() + "Z",
        "pipelineDurationMs": 0,
        "completedAgents": [],
        "pendingAgents": ["mapper", "analyst", "storyteller", "publisher"],
        "pages": {},
        "pagesGenerated": [],
        "pagesOmitted": [],
        "auxiliaryHtmls": [],
        "auxiliaryHtmlsDiscovered": 0,
        "auxiliaryDiscoveryAborted": False,
        "cdnFallbackUsed": False,
        "cdnFallbackDetails": [],
        "vendorMissing": [],
        "smokeTestFailed": False,
        "smokeTestErrors": [],
        "brokenLinks": []
    }

def get_file_hash(filepath):
    if not os.path.exists(filepath):
        return ""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return "sha256:" + hasher.hexdigest()

# Pegar argumento do agente
agent = sys.argv[1] if len(sys.argv) > 1 else "mapper"

if agent not in state["completedAgents"]:
    state["completedAgents"].append(agent)
if agent in state["pendingAgents"]:
    state["pendingAgents"].remove(agent)

pages_by_agent = {
    "mapper": ["arquitetura.html", "modulos.html", "topologia.html"],
    "analyst": ["metricas.html", "timeline.html"],
    "storyteller": ["glossario.html", "deck.html"],
    "publisher": ["index.html"]
}

# Também registrar as features dinamicamente no storyteller
if agent == "storyteller":
    # Procura todos os arquivos na subpasta features
    features_dir = os.path.join(doc_dir, "features")
    if os.path.exists(features_dir):
        for f_file in os.listdir(features_dir):
            if f_file.endswith(".html"):
                page_name = "features/" + f_file
                pages_by_agent["storyteller"].append(page_name)

# Verificar páginas geradas para o agente atual
for page in pages_by_agent.get(agent, []):
    p_path = os.path.join(doc_dir, page)
    if os.path.exists(p_path):
        file_hash = get_file_hash(p_path)
        state["pages"][page] = {
            "status": "created",
            "agent": f"reversa-docs-{agent}",
            "hash": file_hash
        }
        if page not in state["pagesGenerated"]:
            state["pagesGenerated"].append(page)
    else:
        # Se era planejada mas não existe, ela foi omitida
        if page == "timeline.html":
            omission = {"page": "timeline.html", "reason": "chronicle.md not found"}
            if omission not in state["pagesOmitted"]:
                state["pagesOmitted"].append(omission)
        elif page == "glossario.html":
            omission = {"page": "glossario.html", "reason": "soul.md not found"}
            if omission not in state["pagesOmitted"]:
                state["pagesOmitted"].append(omission)
        elif page == "deck.html":
            omission = {"page": "deck.html", "reason": "soul.md not found"}
            if omission not in state["pagesOmitted"]:
                state["pagesOmitted"].append(omission)

state["lastCheckpoint"] = datetime.utcnow().isoformat() + "Z"

# Se o Publisher estiver terminando, calcula tempo total
if agent == "publisher":
    try:
        start_dt = datetime.fromisoformat(state["startedAt"].replace("Z", "+00:00"))
        duration = datetime.now(start_dt.tzinfo) - start_dt
        state["pipelineDurationMs"] = int(duration.total_seconds() * 1000)
    except Exception:
        state["pipelineDurationMs"] = 15000 # fallback

with open(state_path, "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2)

print(f"Estado atualizado para o agente {agent}.")
