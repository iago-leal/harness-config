import os
import pytest
from src.adapters.fs.local import LocalFileSystemAdapter
from src.core.decisions.service import DecisionService

def test_decision_service_load_and_compile(tmp_path):
    fs = LocalFileSystemAdapter()
    service = DecisionService(fs)

    decisoes_dir = os.path.join(tmp_path, "decisoes")
    fs.makedirs(decisoes_dir)

    # Criação do cabeçalho
    header_file = os.path.join(decisoes_dir, "_cabecalho.md")
    fs.write_file(header_file, "# Índice de Microdecisões\nIntrodução curta.")

    # Criando MD-0001 (válido, aponta para MD-0002)
    md1_content = """---
id: MD-0001
gancho: pre-commit
relacoes:
  - depende-de MD-0002
estado: ativo
---

# MD-0001 — Minha Decisão 1
- **D:** ~/.claude
- **PORQUÊ:** single maintainer
- **DESCARTADO:** nada
- **ESTADO:** feito
"""
    fs.write_file(os.path.join(decisoes_dir, "MD-0001.md"), md1_content)

    # Criando MD-0002 (válido)
    md2_content = """---
id: MD-0002
gancho: pre-commit
relacoes: []
estado: ativo
---

# MD-0002 — Minha Decisão 2
- **D:** ~/.claude
- **PORQUÊ:** single maintainer
- **DESCARTADO:** nada
- **ESTADO:** feito
"""
    fs.write_file(os.path.join(decisoes_dir, "MD-0002.md"), md2_content)

    # 1. Carregar decisões
    decisions = service.load_decisions(decisoes_dir)
    assert len(decisions) == 2
    assert decisions[0].id == "MD-0001"
    assert decisions[1].id == "MD-0002"
    assert len(decisions[0].relationships) == 1
    assert decisions[0].relationships[0].rel_type == "depende-de"
    assert decisions[0].relationships[0].target_id == "MD-0002"

    # 2. Validar integridade do Grafo
    errors = service.validate_integrity(decisions)
    assert len(errors) == 0

    # 3. Compilar Índice
    output_index = os.path.join(tmp_path, "microdecisoes.md")
    service.compile_index(decisions, output_index, header_file)

    assert fs.exists(output_index)
    index_content = fs.read_file(output_index)
    
    # Assertiva dos backlinks derivados e conteúdo estruturado
    assert "# Índice de Microdecisões" in index_content
    assert "- **MD-0001** — Minha Decisão 1" in index_content
    assert "- **MD-0002** — Minha Decisão 2" in index_content
    # MD-0001 aponta para MD-0002 (depende-de), logo MD-0002 deve derivar (requerido-por MD-0001)
    assert "depende-de MD-0002" in index_content
    assert "requerido-por MD-0001" in index_content

def test_decision_service_integrity_errors(tmp_path):
    fs = LocalFileSystemAdapter()
    service = DecisionService(fs)

    decisoes_dir = os.path.join(tmp_path, "decisoes")
    fs.makedirs(decisoes_dir)

    # MD-0001 aponta para si mesmo e para MD-0003 (inexistente)
    md1_content = """---
id: MD-0001
gancho: pre-commit
relacoes:
  - refina MD-0001
  - depende-de MD-0003
estado: ativo
---

# MD-0001 — Minha Decisão Errada
- **D:** ~/.claude
- **PORQUÊ:** single maintainer
- **DESCARTADO:** nada
- **ESTADO:** feito
"""
    fs.write_file(os.path.join(decisoes_dir, "MD-0001.md"), md1_content)

    decisions = service.load_decisions(decisoes_dir)
    errors = service.validate_integrity(decisions)

    assert len(errors) == 2
    assert any("Auto-relação inválida" in err for err in errors)
    assert any("Referência órfã" in err for err in errors)
