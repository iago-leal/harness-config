import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

import os
import json
import re

sdd_dir = "/Users/iagoleal/dev/harness/_reversa_sdd"
doc_dir = "/Users/iagoleal/dev/harness/.reversa/documentation"
features_out_dir = os.path.join(doc_dir, "features")

os.makedirs(features_out_dir, exist_ok=True)

# Helper para converter Markdown básico em HTML
def md_to_html(md_text):
    if not md_text:
        return ""
    
    # Escapar HTML básico primeiro
    html = md_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # 1. Code blocks (```lang ... ```)
    code_blocks = []
    def save_code(match):
        code_content = match.group(2)
        code_blocks.append(code_content)
        return f"<!--CODEBLOCK_{len(code_blocks)-1}-->"
    
    html = re.sub(r"```(\w*)\n(.*?)\n```", save_code, html, flags=re.DOTALL)
    
    # 2. Tabelas Markdown
    lines = html.split("\n")
    in_table = False
    table_lines = []
    new_lines = []
    
    for line in lines:
        if re.match(r"^\s*\|.*\|\s*$", line):
            if not in_table:
                in_table = True
                table_lines = [line]
            else:
                table_lines.append(line)
        else:
            if in_table:
                in_table = False
                new_lines.append(render_table(table_lines))
                table_lines = []
            new_lines.append(line)
    if in_table:
        new_lines.append(render_table(table_lines))
        
    html = "\n".join(new_lines)
    
    # 3. Cabeçalhos
    html = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^#### (.*?)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
    
    # 4. Listas
    html = re.sub(r"^\s*[\-\*]\s+(.*?)$", r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"(<li>.*?</li>(?:\n<li>.*?</li>)*)", r"<ul>\1</ul>", html, flags=re.DOTALL)
    
    # 5. Parágrafos
    paragraphs = []
    for line in html.split("\n"):
        line_strip = line.strip()
        if line_strip and not line_strip.startswith("<") and not line_strip.startswith("<!--"):
            paragraphs.append(f"<p>{line}</p>")
        else:
            paragraphs.append(line)
    html = "\n".join(paragraphs)
    
    # 6. Inline: Bold, Italic, Links, Code inline
    html = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', html)
    html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"`(.*?)`", r"<code>\1</code>", html)
    
    # 7. Badges de Rastreabilidade / Prioridade / Confiança
    html = html.replace("🟢", '<span class="badge badge-low">Confirmado</span>')
    html = html.replace("🟡", '<span class="badge badge-medium">Inferido</span>')
    html = html.replace("🔴", '<span class="badge badge-high">Lacuna</span>')
    
    # Restaurar code blocks
    for idx, code in enumerate(code_blocks):
        html = html.replace(f"<!--CODEBLOCK_{idx}-->", f"<pre><code>{code}</code></pre>")
        
    return html

def render_table(table_lines):
    if len(table_lines) < 2:
        return "\n".join(table_lines)
    
    header_line = table_lines[0]
    data_lines = table_lines[2:]
    
    def parse_cells(line):
        cells = line.strip().split("|")
        if cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        return [c.strip() for c in cells]
    
    headers = parse_cells(header_line)
    
    table_html = '<table class="data-table">\n<thead>\n<tr>\n'
    for h in headers:
        table_html += f"<th>{h}</th>\n"
    table_html += "</tr>\n</thead>\n<tbody>\n"
    
    for row in data_lines:
        cells = parse_cells(row)
        table_html += "<tr>\n"
        for c in cells:
            table_html += f"<td>{c}</td>\n"
        if len(cells) < len(headers):
            for _ in range(len(headers) - len(cells)):
                table_html += "<td></td>\n"
        table_html += "</tr>\n"
        
    table_html += "</tbody>\n</table>"
    return table_html

# Encontrar as specs
specs = []
for item in os.listdir(sdd_dir):
    item_path = os.path.join(sdd_dir, item)
    if os.path.isdir(item_path):
        req_path = os.path.join(item_path, "requirements.md")
        if os.path.exists(req_path):
            specs.append(item)

specs.sort()

# Gravar index de features
features_index = {"specs": [{"id": s, "label": s} for s in specs]}
with open(os.path.join(doc_dir, "assets/data/features-index.json"), "w", encoding="utf-8") as f:
    json.dump(features_index, f, indent=2)

# Template base de Feature HTML
feature_tpl = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{LABEL}} | harness</title>
  <meta name="reversa-category" content="feature-spec">
  <meta name="reversa-producer-agent" content="reversa-docs-storyteller">
  <meta name="reversa-template" content="feature">
  <link rel="stylesheet" href="../assets/css/style.css">
  <script src="../assets/js/data.js"></script>
  <script src="../assets/js/nav.js"></script>
  <style>
    .tabs-nav {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.5rem;
    }
    .tab-btn {
      padding: 0.5rem 1rem;
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      border-radius: 6px;
      transition: all 0.2s;
    }
    .tab-btn:hover {
      color: #fff;
      background-color: rgba(255, 255, 255, 0.02);
    }
    .tab-btn.active {
      color: #fff;
      border-color: var(--border-color);
      background-color: var(--panel-bg);
    }
    .tab-content-panel {
      display: none;
      animation: fadeIn 0.2s ease-in-out;
    }
    .tab-content-panel.active {
      display: block;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body data-page-id="feature-{{SLUG}}">
  <!-- Sidebar de Navegação -->
  <aside class="nav-sidebar">
    <div class="brand">
      <div class="brand-logo"></div>
      <div class="brand-title">Harness</div>
    </div>
    <nav class="nav-menu">
      <!-- NAV_LINKS -->
      <span class="placeholder-nav">Carregando menu...</span>
    </nav>
  </aside>

  <!-- Área Principal -->
  <main class="main-content">
    <header>
      <div class="title-area">
        <h1>Feature: {{LABEL}}</h1>
        <p>Especificação funcional, design e tarefas de evolução desta capacidade.</p>
      </div>
      <div class="meta-info">
        Módulo: <code>harness-core</code><br>
        Slug: <code>{{SLUG}}</code>
      </div>
    </header>

    <div class="tabs-nav">
      <button class="tab-btn active" onclick="switchTab('requirements')">📋 Requisitos</button>
      {{DESIGN_TAB}}
      {{TASKS_TAB}}
    </div>

    <!-- Tab Requisitos -->
    <div class="tab-content-panel active" id="tab-requirements">
      <div class="dashboard-card">
        {{REQUIREMENTS_HTML}}
      </div>
    </div>

    {{DESIGN_PANEL}}
    {{TASKS_PANEL}}
  </main>

  <script>
    function switchTab(tabId) {
      document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.classList.remove("active");
      });
      document.querySelectorAll(".tab-content-panel").forEach(panel => {
        panel.classList.remove("active");
      });

      // Ativar botão correspondente
      event.target.classList.add("active");
      // Ativar painel correspondente
      document.getElementById("tab-" + tabId).classList.add("active");
    }
  </script>
</body>
</html>
"""

for slug in specs:
    item_path = os.path.join(sdd_dir, slug)
    
    # 1. Requisitos (Obrigatório)
    req_file = os.path.join(item_path, "requirements.md")
    with open(req_file, "r", encoding="utf-8") as f:
        req_md = f.read()
    req_html = md_to_html(req_md)
    
    # 2. Design (Opcional)
    design_file = os.path.join(item_path, "design.md")
    design_tab = ""
    design_panel = ""
    if os.path.exists(design_file):
        with open(design_file, "r", encoding="utf-8") as f:
            design_md = f.read()
        design_html = md_to_html(design_md)
        design_tab = '<button class="tab-btn" onclick="switchTab(\'design\')">📐 Design Técnico</button>'
        design_panel = f"""
    <!-- Tab Design -->
    <div class="tab-content-panel" id="tab-design">
      <div class="dashboard-card">
        {design_html}
      </div>
    </div>
        """
        
    # 3. Tasks (Opcional)
    tasks_file = os.path.join(item_path, "tasks.md")
    tasks_tab = ""
    tasks_panel = ""
    if os.path.exists(tasks_file):
        with open(tasks_file, "r", encoding="utf-8") as f:
            tasks_md = f.read()
        tasks_html = md_to_html(tasks_md)
        tasks_tab = '<button class="tab-btn" onclick="switchTab(\'tasks\')">🛠️ Roadmap &amp; Tarefas</button>'
        tasks_panel = f"""
    <!-- Tab Tasks -->
    <div class="tab-content-panel" id="tab-tasks">
      <div class="dashboard-card">
        {tasks_html}
      </div>
    </div>
        """
        
    label = slug.replace("-", " ").title()
    
    # Renderizar via replace
    page_html = feature_tpl
    page_html = page_html.replace("{{LABEL}}", label)
    page_html = page_html.replace("{{SLUG}}", slug)
    page_html = page_html.replace("{{REQUIREMENTS_HTML}}", req_html)
    page_html = page_html.replace("{{DESIGN_TAB}}", design_tab)
    page_html = page_html.replace("{{DESIGN_PANEL}}", design_panel)
    page_html = page_html.replace("{{TASKS_TAB}}", tasks_tab)
    page_html = page_html.replace("{{TASKS_PANEL}}", tasks_panel)
    
    # Salvar
    out_page_path = os.path.join(features_out_dir, f"{slug}.html")
    with open(out_page_path, "w", encoding="utf-8") as f:
        f.write(page_html)

print(f"Gerado {len(specs)} páginas de specs de feature.")
