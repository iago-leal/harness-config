"""Contrato de footprint global zero (feature 006).

Garante, de forma barulhenta, que o harness-core só escreve dentro do
repositório do projeto, nunca sob ~/.claude ou ~/.agent-memory.
"""

import os
import pytest

from src.core.decisions.service import DecisionService
from src.core.bootstrap.init_service import InitializationService
from tests.helpers import RecordingFileSystem, FootprintViolation


def test_guard_rejects_write_under_claude():
    fs = RecordingFileSystem(repo_root="/tmp/repo")
    with pytest.raises(FootprintViolation):
        fs.write_file(os.path.expanduser("~/.claude/settings.json"), "x")


def test_guard_rejects_write_under_agent_memory():
    fs = RecordingFileSystem(repo_root="/tmp/repo")
    with pytest.raises(FootprintViolation):
        fs.write_file_atomic(os.path.expanduser("~/.agent-memory/decisoes/x.md"), "x")


def test_guard_rejects_write_outside_repo():
    fs = RecordingFileSystem(repo_root="/tmp/repo")
    with pytest.raises(FootprintViolation):
        fs.write_file("/etc/passwd", "x")


def test_decisions_index_writes_inside_repo(tmp_path):
    # O serviço de decisões escreve o índice dentro do repo, nunca no global.
    fs = RecordingFileSystem(repo_root=str(tmp_path))
    service = DecisionService(fs)
    service.compile_index(
        [], ".harness/microdecisoes.md", ".harness/decisoes/_cabecalho.md"
    )
    # A escrita foi aceita e capturada (não levantou FootprintViolation).
    assert ".harness/microdecisoes.md" in fs.writes
    # Cobertura logada explicitamente: nenhuma escrita global escapou.
    forbidden = os.path.expanduser("~/.claude")
    assert all(
        not os.path.abspath(os.path.join(str(tmp_path), p)).startswith(forbidden)
        for p in fs.writes
    )


def test_gitignore_entry_writes_inside_repo(tmp_path):
    # Feature 011: a escrita da entrada do core no .gitignore do alvo ocorre
    # sob o repositório, jamais em diretório global (RN-N17 estendida).
    fs = RecordingFileSystem(repo_root=str(tmp_path))
    service = InitializationService(fs, None)
    service._ensure_gitignore_entry(str(tmp_path), ".harness/harness-core/")
    gitignore_path = os.path.join(str(tmp_path), ".gitignore")
    # A escrita foi aceita e capturada (não levantou FootprintViolation).
    assert gitignore_path in fs.writes
    assert ".harness/harness-core/" in fs.read_file(gitignore_path)
