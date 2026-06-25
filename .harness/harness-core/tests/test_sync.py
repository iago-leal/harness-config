import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
from src.core.ports.git import GitPort
from src.core.sync.service import SyncService
from tests.helpers import MockFileSystem

def test_sync_service_cache_within_ttl():
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    cache_file = "cache.json"
    service = SyncService(fs, git, cache_filepath=cache_file, cache_ttl_hours=24)

    # Configura cache de 2 horas atrás com commit_hash coincidente com HEAD local
    local_commit = "a" * 40
    last_checked_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    
    fs.write_file(cache_file, f'{{"last_checked_time": "{last_checked_time}", "commit_hash": "{local_commit}"}}')
    
    git.get_head_commit.return_value = local_commit

    # Executa verificação de sincronia
    result = service.check_sync("dummy/repo")
    
    # Deve retornar True e NÃO deve fazer chamada de rede ls-remote (get_remote_commit)
    assert result is True
    git.get_head_commit.assert_called_once_with("dummy/repo")
    git.get_remote_commit.assert_not_called()

def test_sync_service_cache_expired_in_sync():
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    cache_file = "cache.json"
    service = SyncService(fs, git, cache_filepath=cache_file, cache_ttl_hours=24)

    # Configura cache de 26 horas atrás (expirado)
    local_commit = "a" * 40
    last_checked_time = (datetime.now(timezone.utc) - timedelta(hours=26)).isoformat()
    fs.write_file(cache_file, f'{{"last_checked_time": "{last_checked_time}", "commit_hash": "{local_commit}"}}')

    git.get_head_commit.return_value = local_commit
    git.get_remote_commit.return_value = local_commit  # Sincronizado

    result = service.check_sync("dummy/repo")
    
    assert result is True
    git.get_head_commit.assert_called_once_with("dummy/repo")
    git.get_remote_commit.assert_called_once_with("dummy/repo")
    
    # Verifica se atualizou o cache
    assert fs.exists(cache_file)
    cache_content = fs.read_file(cache_file)
    assert local_commit in cache_content

def test_sync_service_cache_expired_out_of_sync():
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    cache_file = "cache.json"
    service = SyncService(fs, git, cache_filepath=cache_file, cache_ttl_hours=24)

    # Cache expirado
    local_commit = "a" * 40
    remote_commit = "b" * 40
    last_checked_time = (datetime.now(timezone.utc) - timedelta(hours=26)).isoformat()
    fs.write_file(cache_file, f'{{"last_checked_time": "{last_checked_time}", "commit_hash": "{local_commit}"}}')

    git.get_head_commit.return_value = local_commit
    git.get_remote_commit.return_value = remote_commit  # Desatualizado

    result = service.check_sync("dummy/repo")
    
    # Deve retornar False (indicando que não está em sync)
    assert result is False
    git.get_head_commit.assert_called_once_with("dummy/repo")
    git.get_remote_commit.assert_called_once_with("dummy/repo")

    # Verifica se salvou o novo remote no cache
    cache_content = fs.read_file(cache_file)
    assert remote_commit in cache_content

def test_sync_service_resilience_on_git_error():
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    cache_file = "cache.json"
    service = SyncService(fs, git, cache_filepath=cache_file, cache_ttl_hours=24)

    # Simula erro de conexão de rede ou do Git na chamada
    git.get_head_commit.side_effect = RuntimeError("Conexão recusada")

    # Deve retornar True (comportamento resiliente de não-bloqueio)
    result = service.check_sync("dummy/repo")
    assert result is True
