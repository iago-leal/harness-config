import toml
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

from src.core.ports.fs import FileSystemPort


class HarnessSection(BaseModel):
    active_harness: Literal["claude", "gemini", "antigravity"] = "claude"
    upstream_path: Optional[str] = None
    # Manter o valor como LITERAL nesta linha: `_get_upstream_version` (012,
    # RN-03) lê a versão do upstream parseando este arquivo por regex.
    version: str = "2.1.0"


# Versão canônica do core, derivada do literal acima — fonte única para o help
# da CLI e para o init_service (feature 020, T018).
CORE_VERSION: str = HarnessSection().version


class FormattingSection(BaseModel):
    exclude_paths: List[str] = Field(default_factory=list)
    opt_out_file: str = ".no-autoformat"


class SyncSection(BaseModel):
    cache_ttl_hours: int = 24
    remote_check_enabled: bool = True


class DecisionsSection(BaseModel):
    dir: str = ".harness/decisoes"
    index_file: str = ".harness/microdecisoes.md"
    header_file: str = ".harness/decisoes/_cabecalho.md"
    # Feature 022: liga o gate de registro de microdecisões (bloqueio no
    # encerrar-sessao, lembrete no Stop do Claude, advisory no Antigravity).
    # Habilitado por padrão; desativável por projeto. Tomls sem o campo herdam True.
    require_registration: bool = True


class SessionSection(BaseModel):
    state_file: str = ".harness/estado-da-sessao.md"
    # Feature 021: quando True, o `cmd resume` anexa o índice de decisões
    # (`decisions.index_file`) ao contexto reinjetado no SessionStart. Habilitado
    # por padrão; desativável por projeto. Tomls sem o campo herdam True.
    inject_decisions_index: bool = True


class RegenSection(BaseModel):
    """Contrato de regeneração de artefatos derivados do projeto (feature 016).

    ``command`` é um comando de shell, declarado pelo dono do projeto, que
    regenera os artefatos derivados (ex.: ``python gerar_site.py && python
    empacotar.py``). Ausente/``None`` → ``cmd regen`` é no-op (exit 0). O core
    não conhece o que cada projeto deriva (baixo acoplamento, RN-N5); só dispara
    o comando declarado, por via única tipada (RN-N16).
    """

    command: Optional[str] = None


class HarnessConfig(BaseModel):
    harness: HarnessSection = Field(default_factory=HarnessSection)
    formatting: FormattingSection = Field(default_factory=FormattingSection)
    sync: SyncSection = Field(default_factory=SyncSection)
    decisions: DecisionsSection = Field(default_factory=DecisionsSection)
    session: SessionSection = Field(default_factory=SessionSection)
    regen: RegenSection = Field(default_factory=RegenSection)


def load_config(fs: FileSystemPort, config_path: str = "harness.toml") -> HarnessConfig:
    """Carrega o harness.toml como HarnessConfig tipado. Arquivo ausente → defaults."""
    if not fs.exists(config_path):
        return HarnessConfig()
    data = toml.loads(fs.read_file(config_path))
    return HarnessConfig(**data)
