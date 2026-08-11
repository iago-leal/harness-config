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


# --------------------------------------------------------------------------- #
# Feature 028 — visão compacta e write-only-when-changed
# --------------------------------------------------------------------------- #


def _write_ficha(fs, decisoes_dir, num, title):
    content = f"""---
id: MD-{num:04d}
gancho: teste
relacoes: []
estado: ativo
---

# MD-{num:04d} — {title}
- **D:** d
- **PORQUÊ:** p
- **DESCARTADO:** nada
- **ESTADO:** feito
"""
    fs.write_file(os.path.join(decisoes_dir, f"MD-{num:04d}.md"), content)


class CountingFS(LocalFileSystemAdapter):
    """Spy fino: registra os alvos de write_file_atomic (WOWC, RF-03)."""

    def __init__(self):
        super().__init__()
        self.atomic_writes = []

    def write_file_atomic(self, path, content):
        self.atomic_writes.append(path)
        super().write_file_atomic(path, content)


def test_compact_view_composicao(tmp_path):
    fs = LocalFileSystemAdapter()
    service = DecisionService(fs)
    decisoes_dir = os.path.join(tmp_path, "decisoes")
    fs.makedirs(decisoes_dir)
    for n in range(1, 5):
        _write_ficha(fs, decisoes_dir, n, f"Decisão {n}")

    decisions = service.load_decisions(decisoes_dir)
    compact_file = os.path.join(tmp_path, "decisoes-recentes.md")
    index_file = os.path.join(tmp_path, "microdecisoes.md")
    service.compile_compact_view(decisions, compact_file, index_file, decisoes_dir, 2)

    content = fs.read_file(compact_file)
    # Cabeçalho de orientação com os ponteiros de consulta sob demanda.
    assert "Não edite à mão" in content
    assert index_file in content
    assert decisoes_dir in content
    # Contagem total do acervo, não só das listadas.
    assert "Total: 4 fichas" in content
    # K=2 mais recentes por ID, a mais nova primeiro, só títulos.
    assert "- **MD-0004** — Decisão 4" in content
    assert "- **MD-0003** — Decisão 3" in content
    assert "MD-0002" not in content
    assert "MD-0001" not in content
    assert content.index("MD-0004") < content.index("MD-0003")
    # Sem backlinks nem relações (metade do peso do índice fica de fora).
    assert "↳" not in content


def test_compact_view_k_zero_degrada_para_ponteiros(tmp_path):
    fs = LocalFileSystemAdapter()
    service = DecisionService(fs)
    decisoes_dir = os.path.join(tmp_path, "decisoes")
    fs.makedirs(decisoes_dir)
    _write_ficha(fs, decisoes_dir, 1, "Única")

    decisions = service.load_decisions(decisoes_dir)
    compact_file = os.path.join(tmp_path, "decisoes-recentes.md")
    service.compile_compact_view(
        decisions, compact_file, os.path.join(tmp_path, "microdecisoes.md"),
        decisoes_dir, 0,
    )

    content = fs.read_file(compact_file)
    assert "Total: 1 ficha" in content
    assert "- **MD-" not in content


def test_compact_view_determinismo_byte_a_byte(tmp_path):
    fs = LocalFileSystemAdapter()
    service = DecisionService(fs)
    decisoes_dir = os.path.join(tmp_path, "decisoes")
    fs.makedirs(decisoes_dir)
    _write_ficha(fs, decisoes_dir, 1, "Decisão 1")
    _write_ficha(fs, decisoes_dir, 2, "Decisão 2")

    decisions = service.load_decisions(decisoes_dir)
    compact_file = os.path.join(tmp_path, "decisoes-recentes.md")
    index_file = os.path.join(tmp_path, "microdecisoes.md")
    service.compile_compact_view(decisions, compact_file, index_file, decisoes_dir, 10)
    primeira = fs.read_file(compact_file)
    service.compile_compact_view(decisions, compact_file, index_file, decisoes_dir, 10)
    assert fs.read_file(compact_file) == primeira


def test_write_only_when_changed_nas_duas_escritas(tmp_path):
    fs = CountingFS()
    service = DecisionService(fs)
    decisoes_dir = os.path.join(tmp_path, "decisoes")
    fs.makedirs(decisoes_dir)
    _write_ficha(fs, decisoes_dir, 1, "Decisão 1")

    index_file = os.path.join(tmp_path, "microdecisoes.md")
    compact_file = os.path.join(tmp_path, "decisoes-recentes.md")

    def _derivar():
        decisions = service.load_decisions(decisoes_dir)
        service.compile_index(decisions, index_file)
        service.compile_compact_view(
            decisions, compact_file, index_file, decisoes_dir, 10
        )

    _derivar()
    assert index_file in fs.atomic_writes
    assert compact_file in fs.atomic_writes

    # Segunda passada sem mudança nas fichas: NENHUMA regravação (RF-03).
    fs.atomic_writes.clear()
    _derivar()
    assert fs.atomic_writes == []

    # Ficha nova: ambas regravam.
    _write_ficha(fs, decisoes_dir, 2, "Decisão 2")
    fs.atomic_writes.clear()
    _derivar()
    assert index_file in fs.atomic_writes
    assert compact_file in fs.atomic_writes
