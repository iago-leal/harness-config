"""Testes da materialização de `.agents/hooks.json` (feature 009, T004).

Cobrem:
- merge do named-hook `harness` preservando chaves de terceiros;
- substituição do placeholder `<ABS>` pelo `command_path` em cada handler;
- nenhuma escrita fora do `project_path` (footprint global zero);
- escrita atômica via `fs.write_file_atomic`.

O `AntigravityProfile` real é fornecido por outra fatia; para desacoplar este
teste da implementação do perfil, injetamos um dublê de perfil que devolve a
STRING JSON pinada (o mesmo contrato esperado de `hooks_block()`). A rotina,
por padrão, usa o `AntigravityProfile` real importado de `harness_profiles`.
"""

import json
import os

import pytest

from src.core.install.antigravity_hooks import materialize_hooks_json
from tests.helpers import MockFileSystem, RecordingFileSystem, FootprintViolation


# STRING JSON pinada (contrato de AntigravityProfile.hooks_block): named-hook
# "harness" com PreToolUse/PostToolUse/Stop e o placeholder literal "<ABS>".
PINNED_HOOKS_BLOCK = json.dumps(
    {
        "harness": {
            "PreToolUse": [
                {
                    "matcher": "write_to_file|replace_file_content|multi_replace_file_content",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "<ABS>/harness agy-hook pre-tool-use",
                            "timeout": 10,
                        }
                    ],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "write_to_file|replace_file_content|multi_replace_file_content",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "<ABS>/harness agy-hook post-tool-use",
                            "timeout": 30,
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "<ABS>/harness agy-hook stop",
                            "timeout": 10,
                        }
                    ]
                }
            ],
        }
    }
)


class StubProfile:
    """Dublê do AntigravityProfile: devolve a STRING JSON pinada."""

    def hooks_block(self) -> str:
        return PINNED_HOOKS_BLOCK


def _hooks_path(project_path: str) -> str:
    return os.path.join(project_path, ".agents", "hooks.json")


def test_materializa_named_hook_harness_em_projeto_vazio():
    fs = MockFileSystem()
    project = "/Users/iagoleal/projeto-x"

    materialize_hooks_json(
        fs, project, "/Users/iagoleal/projeto-x", profile=StubProfile()
    )

    content = fs.read_file(_hooks_path(project))
    data = json.loads(content)
    assert "harness" in data
    assert "PreToolUse" in data["harness"]
    assert "PostToolUse" in data["harness"]
    assert "Stop" in data["harness"]


def test_substitui_ABS_pelo_command_path():
    fs = MockFileSystem()
    project = "/Users/iagoleal/projeto-x"
    command_path = "/abs/path/projeto-x"

    materialize_hooks_json(fs, project, command_path, profile=StubProfile())

    data = json.loads(fs.read_file(_hooks_path(project)))
    commands = []
    for event in data["harness"].values():
        for entry in event:
            for hook in entry["hooks"]:
                commands.append(hook["command"])

    # Nenhum placeholder remanescente; todos resolvidos para command_path.
    assert all("<ABS>" not in c for c in commands)
    assert f"{command_path}/harness agy-hook pre-tool-use" in commands
    assert f"{command_path}/harness agy-hook post-tool-use" in commands
    assert f"{command_path}/harness agy-hook stop" in commands


def test_preserva_chaves_de_terceiros_no_merge():
    project = "/Users/iagoleal/projeto-x"
    existing = {
        "outroPlugin": {"Stop": [{"hooks": [{"type": "command", "command": "x"}]}]},
        "harness": {"VelhoEvento": [{"hooks": []}]},
    }
    fs = MockFileSystem()
    fs.existing_files.add(_hooks_path(project))
    fs.written_files[_hooks_path(project)] = json.dumps(existing)

    materialize_hooks_json(fs, project, "/abs/projeto-x", profile=StubProfile())

    data = json.loads(fs.read_file(_hooks_path(project)))
    # Chave de terceiro intacta.
    assert data["outroPlugin"] == existing["outroPlugin"]
    # named-hook harness substituído pelo bloco canônico (não mantém VelhoEvento).
    assert "VelhoEvento" not in data["harness"]
    assert "PreToolUse" in data["harness"]


def test_escreve_de_forma_atomica():
    class AtomicSpyFS(MockFileSystem):
        def __init__(self):
            super().__init__()
            self.atomic_writes = []

        def write_file_atomic(self, path, content):
            self.atomic_writes.append(path)
            super().write_file_atomic(path, content)

    fs = AtomicSpyFS()
    project = "/Users/iagoleal/projeto-x"

    materialize_hooks_json(fs, project, "/abs/projeto-x", profile=StubProfile())

    assert _hooks_path(project) in fs.atomic_writes


def test_nada_e_escrito_fora_do_project_path():
    project_root = "/Users/iagoleal/projeto-x"
    fs = RecordingFileSystem(repo_root=project_root)

    materialize_hooks_json(fs, project_root, project_root, profile=StubProfile())

    # Toda escrita registrada resolve para dentro do project_path.
    for p in fs.writes:
        abs_p = os.path.abspath(os.path.join(project_root, p))
        assert abs_p == project_root or abs_p.startswith(project_root + os.sep)
    # O hooks.json foi de fato escrito dentro do repositório.
    assert any("hooks.json" in p for p in fs.writes)


def test_escrita_fora_do_repo_e_barulhenta():
    """Sanidade: o guard do footprint dispara se a rotina mirar fora do repo."""
    fs = RecordingFileSystem(repo_root="/Users/iagoleal/projeto-x")
    with pytest.raises(FootprintViolation):
        fs.write_file_atomic("/etc/hooks.json", "x")
