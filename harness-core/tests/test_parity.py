import os
import subprocess
import shutil
import pytest
import re
from src.adapters.fs.local import LocalFileSystemAdapter
from src.core.decisions.service import DecisionService

# Paths
LEGADO_HOOKS_DIR = "/Users/iagoleal/dev/harness/harness-config/hooks"
LEGADO_BIN_DIR = "/Users/iagoleal/dev/harness/harness-config/bin"
NEW_CLI_PATH = "/Users/iagoleal/dev/harness/harness-core/src/main.py"
PYTHON_BIN = "/Users/iagoleal/dev/harness/harness-core/.venv/bin/python3"

def test_parity_format_on_edit_protected_paths(tmp_path):
    # Cenário: Modificações em diretórios protegidos do sistema não sofrem formatação
    # Testa no legado (.sh)
    home = os.path.expanduser("~")
    protected_file = os.path.join(home, ".claude", "settings.json")
    
    # Criamos um arquivo simulado no temp
    test_file = os.path.join(str(tmp_path), "settings.json")
    with open(test_file, 'w') as f:
        f.write("{\n  \"key\": \"val\"\n}")

    # 1. Legado
    legado_script = os.path.join(LEGADO_HOOKS_DIR, "format-on-edit.sh")
    if os.path.exists(legado_script):
        # Passa o arquivo protegido. Deve retornar 0.
        result_legado = subprocess.run(
            [legado_script, protected_file],
            capture_output=True,
            text=True
        )
        assert result_legado.returncode == 0

    # 2. Novo (Python)
    result_new = subprocess.run(
        [PYTHON_BIN, NEW_CLI_PATH, "format", protected_file],
        capture_output=True,
        text=True
    )
    assert result_new.returncode == 0

def test_parity_format_on_edit_opt_out(tmp_path):
    # Cenário: Presença de arquivo no-autoformat na raiz cancela formatação
    # Configura repositório temporário com .no-autoformat
    repo_dir = tmp_path / "repo"
    os.makedirs(repo_dir / ".git") # Simula raiz git
    
    # Cria o .no-autoformat
    with open(repo_dir / ".no-autoformat", 'w') as f:
        f.write("")
        
    test_file = repo_dir / "app.py"
    with open(test_file, 'w') as f:
        f.write("def func():pass\n")

    # 1. Legado (se o script legado checar no-autoformat)
    legado_script = os.path.join(LEGADO_HOOKS_DIR, "format-on-edit.sh")
    if os.path.exists(legado_script):
        result_legado = subprocess.run(
            [legado_script, str(test_file)],
            cwd=str(repo_dir),
            capture_output=True,
            text=True
        )
        assert result_legado.returncode == 0

    # 2. Novo (Python)
    result_new = subprocess.run(
        [PYTHON_BIN, NEW_CLI_PATH, "format", str(test_file)],
        cwd=str(repo_dir),
        capture_output=True,
        text=True
    )
    assert result_new.returncode == 0

def test_parity_decision_graph_backlinks(tmp_path):
    # Cenário: Parser converte metadados textuais e inverte o grafo bidirecionalmente
    decisoes_dir = tmp_path / "decisoes"
    os.makedirs(decisoes_dir)

    # Criação do cabeçalho
    with open(decisoes_dir / "_cabecalho.md", 'w', encoding='utf-8') as f:
        f.write("# Índice de Decisões\n")

    # MD-0002
    md2_content = """---
id: MD-0002
gancho: pre-commit
relacoes: []
estado: ativo
---

# MD-0002 — Decisão 2
- **D:** ~/.claude
- **PORQUÊ:** single
- **DESCARTADO:** nada
- **ESTADO:** feito
"""
    with open(decisoes_dir / "MD-0002.md", 'w', encoding='utf-8') as f:
        f.write(md2_content)

    # MD-0003
    md3_content = """---
id: MD-0003
gancho: pre-commit
relacoes:
  - refina MD-0002
estado: ativo
---

# MD-0003 — Decisão 3
- **D:** ~/.claude
- **PORQUÊ:** single
- **DESCARTADO:** nada
- **ESTADO:** feito
"""
    with open(decisoes_dir / "MD-0003.md", 'w', encoding='utf-8') as f:
        f.write(md3_content)

    # Executa indexador novo Python
    fs = LocalFileSystemAdapter()
    service = DecisionService(fs)
    
    decisions = service.load_decisions(str(decisoes_dir))
    output_new = tmp_path / "microdecisoes_new.md"
    service.compile_index(decisions, str(output_new), str(decisoes_dir / "_cabecalho.md"))
    
    assert os.path.exists(output_new)
    content_new = fs.read_file(str(output_new))
    
    # Valida relações bidirecionais
    assert "refina MD-0002" in content_new
    assert "refinado-por MD-0003" in content_new

def test_parity_interactive_commands_clarify():
    # Cenário: Comando de clarificação bloqueia após a segunda rodada de perguntas
    # Novo Python
    result_new = subprocess.run(
        [PYTHON_BIN, NEW_CLI_PATH, "cmd", "clarificar"],
        capture_output=True,
        text=True
    )
    assert result_new.returncode == 0
    assert "Clarificação de Requisitos" in result_new.stdout
    assert "limitado a no máximo **2 rodadas**" in result_new.stdout
