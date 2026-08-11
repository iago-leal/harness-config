"""Feature 021 — composição do apêndice de decisões no resume.

`build_decisions_appendix` é pura: recebe o `enabled` já calculado pela borda
(que aplica o gate por harness, RN-N5) e não escreve em stderr — a borda cuida
do aviso quando o índice está ausente.
"""

from src.core.session.resume_context import build_decisions_appendix
from tests.helpers import MockFileSystem


def test_appendix_present_when_enabled_and_index_exists():
    fs = MockFileSystem()
    fs.write_file(".harness/microdecisoes.md", "- **MD-0001** — Decisão de teste\n")
    out = build_decisions_appendix(fs, ".harness/microdecisoes.md", True)
    assert "MD-0001" in out
    assert "Índice de decisões" in out
    # O estado vem primeiro; o apêndice começa com separação, para concatenar.
    assert out.startswith("\n")


def test_appendix_empty_when_disabled():
    fs = MockFileSystem()
    fs.write_file(".harness/microdecisoes.md", "- **MD-0001** — Decisão\n")
    assert build_decisions_appendix(fs, ".harness/microdecisoes.md", False) == ""


def test_appendix_empty_when_index_absent():
    fs = MockFileSystem()
    assert build_decisions_appendix(fs, ".harness/microdecisoes.md", True) == ""


# --------------------------------------------------------------------------- #
# Feature 028 — visão compacta com fallback para o índice integral
# --------------------------------------------------------------------------- #


def test_appendix_prefere_visao_compacta_quando_existe():
    fs = MockFileSystem()
    fs.write_file(".harness/microdecisoes.md", "- **MD-0001** — Completa\n")
    fs.write_file(".harness/decisoes-recentes.md", "Total: 1 ficha\n- **MD-0001** — Compacta\n")
    out = build_decisions_appendix(
        fs, ".harness/microdecisoes.md", True,
        compact_file=".harness/decisoes-recentes.md",
    )
    assert "Compacta" in out
    assert "Decisões recentes" in out
    # O índice integral NÃO entra quando a visão compacta existe.
    assert "Completa" not in out
    assert out.startswith("\n")


def test_appendix_fallback_para_indice_quando_compacta_ausente():
    fs = MockFileSystem()
    fs.write_file(".harness/microdecisoes.md", "- **MD-0001** — Completa\n")
    out = build_decisions_appendix(
        fs, ".harness/microdecisoes.md", True,
        compact_file=".harness/decisoes-recentes.md",
    )
    assert "Completa" in out
    assert "Índice de decisões" in out


def test_appendix_fallback_quando_compacta_vazia():
    fs = MockFileSystem()
    fs.write_file(".harness/microdecisoes.md", "- **MD-0001** — Completa\n")
    fs.write_file(".harness/decisoes-recentes.md", "   \n")
    out = build_decisions_appendix(
        fs, ".harness/microdecisoes.md", True,
        compact_file=".harness/decisoes-recentes.md",
    )
    assert "Completa" in out


def test_appendix_disabled_ignora_compacta():
    fs = MockFileSystem()
    fs.write_file(".harness/decisoes-recentes.md", "Total: 1 ficha\n")
    assert (
        build_decisions_appendix(
            fs, ".harness/microdecisoes.md", False,
            compact_file=".harness/decisoes-recentes.md",
        )
        == ""
    )


def test_appendix_vazio_quando_ambos_ausentes():
    fs = MockFileSystem()
    assert (
        build_decisions_appendix(
            fs, ".harness/microdecisoes.md", True,
            compact_file=".harness/decisoes-recentes.md",
        )
        == ""
    )
