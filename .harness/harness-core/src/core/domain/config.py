import toml
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

from src.core.ports.fs import FileSystemPort


class HarnessSection(BaseModel):
    active_harness: Literal["claude", "gemini", "antigravity"] = "claude"
    upstream_path: Optional[str] = None
    # Manter o valor como LITERAL nesta linha: `_get_upstream_version` (012,
    # RN-03) lê a versão do upstream parseando este arquivo por regex.
    version: str = "2.6.2"


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
    # Feature 022 (→025): liga o gate de registro de microdecisões (bloqueio
    # no encerrar-sessao; advisory em stderr no fim de turno de Claude e
    # Antigravity — o soft-block do Stop foi aposentado na MD-0018).
    # Habilitado por padrão; desativável por projeto. Tomls sem o campo herdam True.
    require_registration: bool = True
    # Feature 028: visão compacta do acervo, derivada na MESMA passada que
    # compila o índice completo. É ela que o `cmd resume` injeta no
    # SessionStart (o índice integral vira consulta sob demanda). `ge=0`:
    # teto negativo é erro de configuração barulhento; 0 é válido e degrada
    # para cabeçalho + contagem + ponteiros.
    compact_file: str = ".harness/decisoes-recentes.md"
    compact_index_size: int = Field(default=10, ge=0)


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


class ProgressKanbanSection(BaseModel):
    """Exportador kanban do medidor (feature 027), opt-in por projeto.

    Desligado por padrão: nenhum projeto instalado ganha board sem habilitar
    ``[progress.kanban] enabled = true`` no toml. ``file`` segue a convenção
    do vscode-kanban; o arquivo é derivado no namespace gerenciado (cards
    ``category == "harness"``) e preserva os cards manuais do mantenedor.
    """

    enabled: bool = False
    file: str = ".vscode/vscode-kanban.json"


class ProgressSection(BaseModel):
    """Medidor de progresso de entregáveis (feature 026).

    ``file`` é o artefato DERIVADO gravado por ``harness progress`` — 100%
    recomputável das fontes (ciclo forward do Reversa + estado do harness),
    versionado no git do projeto e sem timestamp de geração (o diff só existe
    quando o estado muda). Tomls sem a seção herdam o default sem migração.
    """

    file: str = ".harness/progresso.md"
    kanban: ProgressKanbanSection = Field(default_factory=ProgressKanbanSection)


class HarnessConfig(BaseModel):
    harness: HarnessSection = Field(default_factory=HarnessSection)
    formatting: FormattingSection = Field(default_factory=FormattingSection)
    sync: SyncSection = Field(default_factory=SyncSection)
    decisions: DecisionsSection = Field(default_factory=DecisionsSection)
    session: SessionSection = Field(default_factory=SessionSection)
    regen: RegenSection = Field(default_factory=RegenSection)
    progress: ProgressSection = Field(default_factory=ProgressSection)


def load_config(fs: FileSystemPort, config_path: str = "harness.toml") -> HarnessConfig:
    """Carrega o harness.toml como HarnessConfig tipado. Arquivo ausente → defaults."""
    if not fs.exists(config_path):
        return HarnessConfig()
    data = toml.loads(fs.read_file(config_path))
    return HarnessConfig(**data)
