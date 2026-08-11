"""Testes de ``src/core/progress/stages.py`` (feature 026, D-04).

Fixam a PARIDADE com a tabela de estágio físico e a regra de contagem de
checkboxes do skill ``reversa-requirements`` (seção "Detecção de feature em
andamento"), inclusive a pegadinha do formato real: o checkbox das tabelas de
``actions.md`` vem envolto em crase (`` `[X]` ``).
"""

from src.core.progress import stages


class DirFs:
    """FS mínimo por dicionário: chave = caminho relativo, valor = conteúdo."""

    def __init__(self, files=None):
        self.files = dict(files or {})

    def exists(self, path):
        p = path.rstrip("/")
        return p in self.files or any(k.startswith(p + "/") for k in self.files)

    def read_file(self, path):
        return self.files[path]


ACTIONS_MISTO = """# Actions: exemplo

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 3 |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | faz algo | - | `[//]` | `a.py` | 🟢 | `[X]` |
| T002 | faz outra coisa | T001 | - | `b.py` | 🟢 | `[ ]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | testa sem crase | - | - | c.py | 🟢 | [ ] |

## Notas de execução

- [ ] item de lista livre não conta como ação
Linha de texto solto também não conta.
"""

ACTIONS_TUDO_FECHADO = ACTIONS_MISTO.replace("`[ ]`", "`[X]`").replace(
    "| [ ] |", "| [X] |"
)


def _feature(files):
    return DirFs({f"_fwd/026-x/{nome}": corpo for nome, corpo in files.items()})


def test_estagio_vazio_sem_requirements():
    fs = _feature({"outra-coisa.md": "x"})
    assert stages.detectar_estagio(fs, "_fwd/026-x") == "vazio"


def test_estagio_requirements_sem_roadmap():
    fs = _feature({"requirements.md": "# r"})
    assert stages.detectar_estagio(fs, "_fwd/026-x") == "requirements"


def test_estagio_plan_sem_actions():
    fs = _feature({"requirements.md": "# r", "roadmap.md": "# p"})
    assert stages.detectar_estagio(fs, "_fwd/026-x") == "plan"


def test_estagio_coding_com_checkbox_aberto():
    fs = _feature(
        {"requirements.md": "# r", "roadmap.md": "# p", "actions.md": ACTIONS_MISTO}
    )
    assert stages.detectar_estagio(fs, "_fwd/026-x") == "coding-em-progresso"


def test_estagio_done_com_tudo_fechado():
    fs = _feature(
        {
            "requirements.md": "# r",
            "roadmap.md": "# p",
            "actions.md": ACTIONS_TUDO_FECHADO,
        }
    )
    assert stages.detectar_estagio(fs, "_fwd/026-x") == "done"


def test_actions_sem_linhas_de_acao_conta_como_plan():
    # actions.md presente mas ainda sem nenhuma linha de checkbox: o trabalho
    # de decomposição não terminou, o estágio físico permanece `plan`.
    fs = _feature(
        {
            "requirements.md": "# r",
            "roadmap.md": "# p",
            "actions.md": "# Actions\n\nSó prosa, sem tabela.\n",
        }
    )
    assert stages.detectar_estagio(fs, "_fwd/026-x") == "plan"


def test_contagem_global_ignora_cabecalhos_e_texto_livre():
    assert stages.contar_checkboxes(ACTIONS_MISTO) == (1, 3)


def test_contagem_aceita_checkbox_com_e_sem_crase():
    feitas, total = stages.contar_checkboxes(
        "| T001 | a | - | - | x | 🟢 | `[X]` |\n| T002 | b | - | - | y | 🟢 | [X] |\n"
    )
    assert (feitas, total) == (2, 2)


def test_contagem_por_fase_na_ordem_do_documento():
    assert stages.contar_por_fase(ACTIONS_MISTO) == [
        ("Fase 1, Preparação", 1, 2),
        ("Fase 2, Testes", 0, 1),
    ]


def test_contagem_por_fase_ignora_secoes_sem_acoes():
    fases = [f for f, _, _ in stages.contar_por_fase(ACTIONS_MISTO)]
    assert "Resumo" not in fases
    assert "Notas de execução" not in fases
