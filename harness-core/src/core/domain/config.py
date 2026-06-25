import toml
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

from src.core.ports.fs import FileSystemPort


class HarnessSection(BaseModel):
    active_harness: Literal["claude", "gemini", "antigravity"] = "claude"
    upstream_path: Optional[str] = None
    version: str = "1.2.45"


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


class SessionSection(BaseModel):
    state_file: str = ".harness/estado-da-sessao.md"


class HarnessConfig(BaseModel):
    harness: HarnessSection = Field(default_factory=HarnessSection)
    formatting: FormattingSection = Field(default_factory=FormattingSection)
    sync: SyncSection = Field(default_factory=SyncSection)
    decisions: DecisionsSection = Field(default_factory=DecisionsSection)
    session: SessionSection = Field(default_factory=SessionSection)


def load_config(fs: FileSystemPort, config_path: str = "harness.toml") -> HarnessConfig:
    """Carrega o harness.toml como HarnessConfig tipado. Arquivo ausente → defaults."""
    if not fs.exists(config_path):
        return HarnessConfig()
    data = toml.loads(fs.read_file(config_path))
    return HarnessConfig(**data)
