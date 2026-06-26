"""Detecção das ofertas de fim de sessão (feature 014).

Serviço de domínio puro: dado o repositório e a config, decide *o que* oferecer
ao encerrar a sessão — publicar o trabalho (push) e/ou atualizar o núcleo
(upgrade) —, devolvendo modelos de valor que a borda consome para interagir. A
detecção é resiliente: qualquer falha de git/rede degrada para "sem oferta"
(campo ``None``), nunca levantando para a borda (RN-02/RN-03/RN-09).

O domínio fala com git apenas pela porta ``GitPort`` (RN-N5) e com o upstream
apenas pelo ``SyncService``; não conhece terminal nem o harness ativo.
"""

from dataclasses import dataclass
from typing import Optional

from src.core.ports.git import GitPort
from src.core.sync.service import SyncService


@dataclass
class PushOffer:
    """Oferta de publicar o trabalho do branch corrente."""

    branch: str
    ahead: int
    is_default_branch: bool
    remote: str = "origin"


@dataclass
class UpgradeOffer:
    """Oferta de atualizar o Harness Core a partir do upstream."""

    current_version: str
    target_version: str
    upstream_path: str


@dataclass
class EndSessionOffers:
    """Agregado das ofertas; campos ``None`` quando a oferta não se aplica."""

    push: Optional[PushOffer] = None
    upgrade: Optional[UpgradeOffer] = None

    @property
    def has_any(self) -> bool:
        return self.push is not None or self.upgrade is not None


class EndSessionOffersService:
    def __init__(self, git: GitPort, sync: SyncService):
        self.git = git
        self.sync = sync

    def detect(self, repo_path: str, config) -> EndSessionOffers:
        """Monta as ofertas cabíveis. Ordem de uso pela borda: push → upgrade."""
        return EndSessionOffers(
            push=self._detect_push(repo_path),
            upgrade=self._detect_upgrade(repo_path, config),
        )

    def _detect_push(self, repo_path: str) -> Optional[PushOffer]:
        # Só há push a oferecer com upstream tracking E commits à frente. Sem
        # tracking, count_commits_ahead já devolve 0 (RN-04/RN-11).
        try:
            ahead = self.git.count_commits_ahead(repo_path)
            if ahead <= 0:
                return None
            branch = self.git.get_current_branch(repo_path)
            default = self.git.get_default_branch(repo_path)
            return PushOffer(
                branch=branch,
                ahead=ahead,
                is_default_branch=(branch == default),
            )
        except Exception:
            return None

    def _detect_upgrade(self, repo_path: str, config) -> Optional[UpgradeOffer]:
        upstream_path = config.harness.upstream_path
        if not upstream_path:
            return None
        try:
            target = self.sync.check_version_update_remote(
                config.harness.version, upstream_path
            )
        except Exception:
            return None
        if not target:
            return None
        return UpgradeOffer(
            current_version=config.harness.version,
            target_version=target,
            upstream_path=upstream_path,
        )
