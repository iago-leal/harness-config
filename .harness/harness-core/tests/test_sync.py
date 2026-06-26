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

    fs.write_file(
        cache_file,
        f'{{"last_checked_time": "{last_checked_time}", "commit_hash": "{local_commit}"}}',
    )

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
    fs.write_file(
        cache_file,
        f'{{"last_checked_time": "{last_checked_time}", "commit_hash": "{local_commit}"}}',
    )

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
    fs.write_file(
        cache_file,
        f'{{"last_checked_time": "{last_checked_time}", "commit_hash": "{local_commit}"}}',
    )

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


def test_check_version_update_resolves_legacy_layout():
    # Feature 012: a checagem passiva varre os caminhos-candidato. Mesmo que o
    # upstream esteja no layout legado (core na raiz), o alerta de nova versão
    # sobrevive ao relayout.
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    service = SyncService(fs, git, cache_filepath="cache.json")

    fs.write_file(
        "/up/harness-core/src/core/domain/config.py", 'version: str = "2.0.0"'
    )

    assert service.check_version_update("1.0.0", "/up") == "2.0.0"
    # Mesma versão -> sem alerta.
    assert service.check_version_update("2.0.0", "/up") is None


def test_check_version_update_returns_none_when_no_candidate():
    # Feature 012: a checagem passiva é não-bloqueante — sem candidato, devolve
    # None em silêncio (diferente do upgrade, que aborta barulhento).
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    service = SyncService(fs, git, cache_filepath="cache.json")

    assert service.check_version_update("1.0.0", "/up") is None


# --- Comparação de versão REMOTA (feature 014) ----------------------------


def test_check_version_update_remote_aponta_para_publicado():
    # Versão publicada no remoto do upstream à frente da local → devolve o alvo,
    # e a rede foi consultada (fetch).
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    git.get_default_branch.return_value = "main"
    git.get_file_at_ref.return_value = 'version: str = "2.0.0"'
    service = SyncService(fs, git, cache_filepath="cache.json")

    assert service.check_version_update_remote("1.0.0", "/up") == "2.0.0"
    git.fetch.assert_called_once()
    git.get_file_at_ref.assert_called()


def test_check_version_update_remote_igual_devolve_none():
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    git.get_default_branch.return_value = "main"
    git.get_file_at_ref.return_value = 'version: str = "1.0.0"'
    service = SyncService(fs, git, cache_filepath="cache.json")

    assert service.check_version_update_remote("1.0.0", "/up") is None


def test_check_version_update_remote_resiliente_a_falha_de_rede():
    # fetch falhando (offline/credencial) → None, sem propagar exceção.
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    git.fetch.side_effect = RuntimeError("offline")
    service = SyncService(fs, git, cache_filepath="cache.json")

    assert service.check_version_update_remote("1.0.0", "/up") is None


def test_check_version_update_remote_sem_upstream_devolve_none():
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    service = SyncService(fs, git, cache_filepath="cache.json")

    assert service.check_version_update_remote("1.0.0", None) is None
    git.fetch.assert_not_called()
