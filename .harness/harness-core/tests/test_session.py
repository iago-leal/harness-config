import pytest
from datetime import datetime, timezone

from src.core.domain.models import SessionState, SessionNarrative
from src.core.session import serializer
from src.core.session.errors import MalformedSessionStateError


def _state(**kw):
    base = dict(
        commit_hash="a" * 40,
        active_feature="feat-x",
        start_time=datetime(2026, 6, 23, 18, 0, 0, tzinfo=timezone.utc),
        is_active=True,
    )
    base.update(kw)
    return SessionState(**base)


def test_round_trip_without_narrative():
    s = _state()
    parsed = serializer.parse(serializer.render(s))
    assert parsed.commit_hash == s.commit_hash
    assert parsed.active_feature == s.active_feature
    assert parsed.is_active is True
    assert parsed.start_time == s.start_time
    assert parsed.narrative.feito == []


def test_round_trip_with_narrative():
    nar = SessionNarrative(
        feito=["fez x", "fez y"],
        proximos_passos=["fazer z"],
        pendencias=["bloqueio w"],
        ponteiros=["MD-0002"],
    )
    s = _state(narrative=nar, is_active=False)
    parsed = serializer.parse(serializer.render(s))
    assert parsed.narrative.feito == ["fez x", "fez y"]
    assert parsed.narrative.proximos_passos == ["fazer z"]
    assert parsed.narrative.pendencias == ["bloqueio w"]
    assert parsed.narrative.ponteiros == ["MD-0002"]
    assert parsed.is_active is False


def test_parse_without_frontmatter_raises():
    with pytest.raises(MalformedSessionStateError):
        serializer.parse("sem front-matter nenhum aqui")


def test_parse_missing_fields_raises():
    bad = "---\ncommit: " + "a" * 40 + "\n---\n\n## Ponteiros\n"
    with pytest.raises(MalformedSessionStateError):
        serializer.parse(bad)


def test_parse_invalid_commit_raises():
    bad = (
        "---\ncommit: nao-e-sha1\nfeature: f\n"
        "start_time: 2026-06-23T18:00:00+00:00\nstatus: active\n---\n\n"
    )
    with pytest.raises(MalformedSessionStateError):
        serializer.parse(bad)


def test_parse_estado_inicial_vazio_retorna_none():
    # Template que o `init` grava: os 4 campos obrigatórios null. Equivale a
    # "sem sessão" (como arquivo ausente), não a corrupção — retorna None.
    inicial = (
        "---\ncommit: null\nfeature: null\n"
        "start_time: null\nstatus: null\n---\n# Estado de Sessão\n"
    )
    assert serializer.parse(inicial) is None


def test_parse_nulo_parcial_ainda_malformado():
    # Nulo PARCIAL não é o sentinela inicial: o barulho do RN-N4 é preservado.
    bad = "---\ncommit: null\nfeature: null\nstart_time: null\nstatus: active\n---\n\n"
    with pytest.raises(MalformedSessionStateError):
        serializer.parse(bad)


def test_round_trip_com_fingerprints_do_gate():
    # Feature 022: os fingerprints do gate sobrevivem ao round-trip (RN-N2).
    s = _state(
        gate_lembrete_fingerprint="1" * 40,
        gate_encerramento_fingerprint="2" * 40,
    )
    parsed = serializer.parse(serializer.render(s))
    assert parsed.gate_lembrete_fingerprint == "1" * 40
    assert parsed.gate_encerramento_fingerprint == "2" * 40


def test_parse_estado_pre_022_sem_fingerprints_vira_none():
    # Retrocompatível: estado gravado antes da 022 (sem os campos) → None.
    texto = (
        "---\ncommit: " + "a" * 40 + "\nfeature: f\n"
        "start_time: 2026-06-23T18:00:00+00:00\nstatus: active\n---\n\n"
    )
    parsed = serializer.parse(texto)
    assert parsed.gate_lembrete_fingerprint is None
    assert parsed.gate_encerramento_fingerprint is None


def test_render_sem_fingerprints_nao_emite_campos():
    # Sem gate acionado, o arquivo permanece idêntico ao formato pré-022.
    texto = serializer.render(_state())
    assert "gate_lembrete_fingerprint" not in texto
    assert "gate_encerramento_fingerprint" not in texto
