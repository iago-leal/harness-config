import pytest
from src.core.domain.models import (
    Relationship,
    Decision,
    SessionState,
    SessionNarrative,
)
from src.core.domain.config import HarnessConfig, load_config
from tests.helpers import MockFileSystem


def test_relationship_validation():
    # Relação válida
    rel = Relationship(rel_type="refina", target_id="MD-0002")
    assert rel.rel_type == "refina"
    assert rel.target_id == "MD-0002"

    # Tipo inválido
    with pytest.raises(ValueError):
        Relationship(rel_type="invalido", target_id="MD-0002")

    # ID inválido
    with pytest.raises(ValueError):
        Relationship(rel_type="refina", target_id="invalid-id")


def test_decision_validation():
    # ID válido
    dec = Decision(id="MD-0001", gancho="pre-commit", status="ativo")
    assert dec.id == "MD-0001"

    # ID inválido
    with pytest.raises(ValueError):
        Decision(id="invalid-id", gancho="pre-commit")


def test_decision_add_relationship():
    dec = Decision(id="MD-0001", gancho="pre-commit")
    dec.add_relationship("refina", "MD-0002")
    assert len(dec.relationships) == 1
    assert dec.relationships[0].rel_type == "refina"
    assert dec.relationships[0].target_id == "MD-0002"


def test_decision_integrity_validation():
    # Markdown válido contendo H1 e as 4 seções
    valid_md = """# MD-0001 — Repositório próprio privado
- **D:** ~/.claude é um repo git
- **PORQUÊ:** single maintainer
- **DESCARTADO:** repo público
- **ESTADO:** feito
"""
    dec = Decision(id="MD-0001", gancho="pre-commit", raw_content=valid_md)
    errors = dec.validate_integrity()
    assert len(errors) == 0

    # Markdown inválido (sem PORQUÊ)
    invalid_md = """# MD-0001 — Repositório próprio privado
- **D:** ~/.claude é um repo git
- **DESCARTADO:** repo público
- **ESTADO:** feito
"""
    dec_invalid = Decision(id="MD-0001", gancho="pre-commit", raw_content=invalid_md)
    errors = dec_invalid.validate_integrity()
    assert len(errors) == 1
    assert "PORQUÊ" in errors[0]


def test_session_state_lifecycle():
    initial_hash = "a" * 40
    session = SessionState(commit_hash=initial_hash, active_feature="feat-1")
    assert session.is_active is True

    # Fechar sessão
    new_hash = "b" * 40
    session.close_session(new_hash)
    assert session.is_active is False
    assert session.commit_hash == new_hash

    # Iniciar nova sessão
    session.start_session("feat-2", initial_hash)
    assert session.is_active is True
    assert session.active_feature == "feat-2"
    assert session.commit_hash == initial_hash


def test_session_narrative():
    nar = SessionNarrative()
    assert nar.feito == []
    assert nar.is_empty()

    nar2 = SessionNarrative(feito=["fez x"], ponteiros=["MD-0002"])
    assert not nar2.is_empty()
    assert nar2.feito == ["fez x"]

    # SessionState ganha narrativa por padrão, sem quebrar a construção existente
    state = SessionState(commit_hash="a" * 40, active_feature="f")
    assert state.narrative.is_empty()


def test_decisions_config_defaults():
    # Os caminhos de decisão moram em .harness/ por padrão (feature 005).
    cfg = HarnessConfig()
    assert cfg.decisions.dir == ".harness/decisoes"
    assert cfg.decisions.index_file == ".harness/microdecisoes.md"
    assert cfg.decisions.header_file == ".harness/decisoes/_cabecalho.md"


def test_load_config_decisions_override():
    # [decisions] no harness.toml sobrescreve apenas os campos presentes.
    fs = MockFileSystem()
    fs.write_file("harness.toml", '[decisions]\ndir = "custom/dec"\n')
    cfg = load_config(fs)
    assert cfg.decisions.dir == "custom/dec"
    assert cfg.decisions.index_file == ".harness/microdecisoes.md"


def test_load_config_absent_uses_decisions_defaults():
    cfg = load_config(MockFileSystem())
    assert cfg.decisions.dir == ".harness/decisoes"
