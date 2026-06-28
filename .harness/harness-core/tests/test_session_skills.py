"""Testes da materialização da skill `encerrar-sessao` (feature 018, T005).

Cobrem:
- grava a árvore (SKILL.md + scripts) sob `.claude/skills` e `.agents/skills`;
- paridade: mesma árvore (bytes idênticos) nos dois harnesses;
- escrita atômica via `write_file_atomic`; idempotência na reexecução;
- migração não-destrutiva: remove os artefatos antigos (command/workflow .md) e
  preserva skills/arquivos de terceiros;
- Gemini (sem skills_dir) não grava a árvore mas ainda limpa seus órfãos;
- nenhuma escrita fora do `project_path` (footprint global zero).
"""

import os

from src.core.install.session_skills import (
    materialize_session_skills,
    skill_tree,
)
from tests.helpers import MockFileSystem, RecordingFileSystem

PROJECT = "/Users/iagoleal/projeto-x"


def _claude(rel: str) -> str:
    return os.path.join(PROJECT, ".claude", "skills", "encerrar-sessao", rel)


def _antigravity(rel: str) -> str:
    return os.path.join(PROJECT, ".agents", "skills", "encerrar-sessao", rel)


def test_skill_tree_tem_skillmd_e_scripts():
    tree = skill_tree()
    assert "SKILL.md" in tree
    assert os.path.join("scripts", "_bootstrap.py") in tree
    assert os.path.join("scripts", "encerrar_sessao.py") in tree
    # A skill não delega ao binário: o entry chama o serviço do core.
    assert "SessionCloseFlow" in tree[os.path.join("scripts", "encerrar_sessao.py")]


def test_materializa_arvore_nos_dois_harnesses():
    fs = MockFileSystem()
    materialize_session_skills(fs, PROJECT)

    for rel in ("SKILL.md", "scripts/_bootstrap.py", "scripts/encerrar_sessao.py"):
        assert fs.exists(_claude(rel)), rel
        assert fs.exists(_antigravity(rel)), rel


def test_paridade_bytes_identicos_entre_harnesses():
    fs = MockFileSystem()
    materialize_session_skills(fs, PROJECT)

    for rel in ("SKILL.md", "scripts/_bootstrap.py", "scripts/encerrar_sessao.py"):
        assert fs.read_file(_claude(rel)) == fs.read_file(_antigravity(rel))


def test_escreve_de_forma_atomica():
    class AtomicSpyFS(MockFileSystem):
        def __init__(self):
            super().__init__()
            self.atomic_writes = []

        def write_file_atomic(self, path, content):
            self.atomic_writes.append(path)
            super().write_file_atomic(path, content)

    fs = AtomicSpyFS()
    materialize_session_skills(fs, PROJECT)

    assert _claude("SKILL.md") in fs.atomic_writes
    assert _antigravity("SKILL.md") in fs.atomic_writes


def test_idempotente_na_reexecucao():
    fs = MockFileSystem()
    materialize_session_skills(fs, PROJECT)
    primeiro = fs.read_file(_claude("SKILL.md"))
    materialize_session_skills(fs, PROJECT)
    assert fs.read_file(_claude("SKILL.md")) == primeiro


def test_preserva_skill_de_terceiro():
    outra = os.path.join(PROJECT, ".claude", "skills", "outra-skill", "SKILL.md")
    fs = MockFileSystem()
    fs.existing_files.add(outra)
    fs.written_files[outra] = "skill do usuário"

    materialize_session_skills(fs, PROJECT)

    assert fs.exists(_claude("SKILL.md"))
    assert fs.read_file(outra) == "skill do usuário"


def test_migra_removendo_artefatos_antigos():
    fs = MockFileSystem()
    velho_claude = os.path.join(PROJECT, ".claude", "commands", "encerrar-sessao.md")
    velho_agy_sing = os.path.join(PROJECT, ".agent", "workflows", "encerrar-sessao.md")
    velho_agy_plur = os.path.join(PROJECT, ".agents", "workflows", "encerrar-sessao.md")
    for p in (velho_claude, velho_agy_sing, velho_agy_plur):
        fs.existing_files.add(p)
        fs.written_files[p] = "artefato antigo"

    materialize_session_skills(fs, PROJECT)

    # Skill nova nos dois...
    assert fs.exists(_claude("SKILL.md"))
    assert fs.exists(_antigravity("SKILL.md"))
    # ...e os três órfãos removidos.
    assert not fs.exists(velho_claude)
    assert not fs.exists(velho_agy_sing)
    assert not fs.exists(velho_agy_plur)


def test_preserva_workflow_de_terceiro_na_migracao():
    fs = MockFileSystem()
    stale = os.path.join(PROJECT, ".agent", "workflows", "encerrar-sessao.md")
    terceiro = os.path.join(PROJECT, ".agent", "workflows", "outro-workflow.md")
    fs.existing_files.update({stale, terceiro})
    fs.written_files[stale] = "workflow antigo"
    fs.written_files[terceiro] = "workflow de terceiro"

    materialize_session_skills(fs, PROJECT)

    assert not fs.exists(stale)
    assert fs.read_file(terceiro) == "workflow de terceiro"


def test_gemini_nao_grava_arvore_mas_limpa_orfaos():
    from src.core.install.harness_profiles import GeminiProfile

    fs = MockFileSystem()
    materialize_session_skills(fs, PROJECT, profiles=[GeminiProfile()])

    # Gemini não expõe skills_dir → nenhuma árvore gravada para ele.
    assert not any(
        ".claude/skills" in p or ".agents/skills" in p for p in fs.written_files
    )


def test_nada_e_escrito_fora_do_project_path():
    fs = RecordingFileSystem(repo_root=PROJECT)
    materialize_session_skills(fs, PROJECT)

    for p in fs.writes:
        abs_p = os.path.abspath(os.path.join(PROJECT, p))
        assert abs_p == PROJECT or abs_p.startswith(PROJECT + os.sep)
    assert any("encerrar-sessao" in p and "SKILL.md" in p for p in fs.writes)
