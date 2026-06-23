from pydantic import BaseModel, Field
from typing import List, Literal


class HarnessSection(BaseModel):
    active_harness: Literal["claude", "gemini", "antigravity"] = "claude"


class FormattingSection(BaseModel):
    exclude_paths: List[str] = Field(default_factory=list)
    opt_out_file: str = ".no-autoformat"


class SyncSection(BaseModel):
    cache_ttl_hours: int = 24
    remote_check_enabled: bool = True


class HarnessConfig(BaseModel):
    harness: HarnessSection = Field(default_factory=HarnessSection)
    formatting: FormattingSection = Field(default_factory=FormattingSection)
    sync: SyncSection = Field(default_factory=SyncSection)


def load_config(fs: FileSystemPort, config_path: str = "harness.toml") -> HarnessConfig:
    """Carrega o harness.toml como HarnessConfig tipado. Arquivo ausente → defaults."""
    if not fs.exists(config_path):
        return HarnessConfig()
    data = toml.loads(fs.read_file(config_path))
    return HarnessConfig(**data)
