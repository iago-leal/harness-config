from unittest.mock import MagicMock

from src.core.ports.git import GitPort
from src.core.sync.service import SyncService
from src.core.domain.config import HarnessConfig, HarnessSection
from src.core.session.offers import EndSessionOffersService


def _config(upstream_path=None, version="1.0.0"):
    return HarnessConfig(
        harness=HarnessSection(upstream_path=upstream_path, version=version)
    )


def test_push_offer_quando_ha_commits_a_frente():
    git = MagicMock(spec=GitPort)
    git.count_commits_ahead.return_value = 2
    git.get_current_branch.return_value = "feature-x"
    git.get_default_branch.return_value = "main"
    sync = MagicMock(spec=SyncService)
    service = EndSessionOffersService(git, sync)

    offers = service.detect("repo", _config(upstream_path=None))

    assert offers.push is not None
    assert offers.push.branch == "feature-x"
    assert offers.push.ahead == 2
    assert offers.push.is_default_branch is False
    assert offers.upgrade is None  # sem upstream_path


def test_sem_commits_a_frente_nao_oferece_push():
    git = MagicMock(spec=GitPort)
    git.count_commits_ahead.return_value = 0
    sync = MagicMock(spec=SyncService)
    service = EndSessionOffersService(git, sync)

    offers = service.detect("repo", _config())

    assert offers.push is None


def test_branch_principal_marca_is_default():
    git = MagicMock(spec=GitPort)
    git.count_commits_ahead.return_value = 1
    git.get_current_branch.return_value = "main"
    git.get_default_branch.return_value = "main"
    sync = MagicMock(spec=SyncService)
    service = EndSessionOffersService(git, sync)

    offers = service.detect("repo", _config())

    assert offers.push is not None
    assert offers.push.is_default_branch is True


def test_upgrade_offer_quando_upstream_a_frente():
    git = MagicMock(spec=GitPort)
    git.count_commits_ahead.return_value = 0
    sync = MagicMock(spec=SyncService)
    sync.check_version_update_remote.return_value = "2.0.0"
    service = EndSessionOffersService(git, sync)

    offers = service.detect("repo", _config(upstream_path="/up", version="1.0.0"))

    assert offers.upgrade is not None
    assert offers.upgrade.current_version == "1.0.0"
    assert offers.upgrade.target_version == "2.0.0"
    assert offers.upgrade.upstream_path == "/up"


def test_upgrade_none_quando_versoes_iguais():
    git = MagicMock(spec=GitPort)
    git.count_commits_ahead.return_value = 0
    sync = MagicMock(spec=SyncService)
    sync.check_version_update_remote.return_value = None
    service = EndSessionOffersService(git, sync)

    offers = service.detect("repo", _config(upstream_path="/up", version="2.0.0"))

    assert offers.upgrade is None


def test_falha_de_git_degrada_push_para_none():
    git = MagicMock(spec=GitPort)
    git.count_commits_ahead.side_effect = RuntimeError("git quebrou")
    sync = MagicMock(spec=SyncService)
    service = EndSessionOffersService(git, sync)

    offers = service.detect("repo", _config())

    # Degrada sem propagar exceção (RN-02).
    assert offers.push is None
    assert offers.has_any is False
