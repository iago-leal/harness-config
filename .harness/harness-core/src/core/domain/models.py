import re
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Relationship(BaseModel):
    rel_type: str
    target_id: str

    @field_validator("rel_type")
    @classmethod
    def validate_rel_type(cls, value: str) -> str:
        valid_types = {
            "depende-de",
            "substitui",
            "refina",
            "relaciona",
            "estende",
            "bloqueia",
        }
        if value.lower() not in valid_types:
            raise ValueError(
                f"Tipo de relação inválido: {value}. Deve ser um de {valid_types}"
            )
        return value.lower()

    @field_validator("target_id")
    @classmethod
    def validate_target_id(cls, value: str) -> str:
        if not re.match(r"^MD-\d{4}$", value):
            raise ValueError(
                f"ID alvo inválido: {value}. Deve seguir o formato MD-XXXX"
            )
        return value


class Decision(BaseModel):
    id: str
    gancho: str
    status: str = "ativo"  # ativo | descartado
    relationships: List[Relationship] = Field(default_factory=list)
    filepath: Optional[str] = None
    raw_content: Optional[str] = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not re.match(r"^MD-\d{4}$", value):
            raise ValueError(f"ID inválido: {value}. Deve seguir o formato MD-XXXX")
        return value

    def add_relationship(self, rel_type: str, target: str):
        rel = Relationship(rel_type=rel_type, target_id=target)
        self.relationships.append(rel)

    def validate_integrity(self) -> List[str]:
        """
        Valida a integridade semântica da ficha de decisão baseada no seu conteúdo markdown.
        Retorna uma lista de strings contendo erros encontrados. Se vazia, a decisão é válida.
        """
        errors = []
        if not self.raw_content:
            errors.append("Ficha sem conteúdo raw_content carregado.")
            return errors

        # Validar cabeçalho H1 com o ID correto
        h1_pattern = rf"^#\s+{self.id}\b"
        if not re.search(h1_pattern, self.raw_content, re.MULTILINE):
            errors.append(
                f"Cabeçalho H1 com o ID '{self.id}' não encontrado no Markdown."
            )

        required_patterns = {
            "D": r"-\s+\*\*D:?\*\*:?",
            "PORQUÊ": r"-\s+\*\*PORQUÊ:?\*\*:?",
            "DESCARTADO": r"-\s+\*\*DESCARTADO:?\*\*:?",
            "ESTADO": r"-\s+\*\*ESTADO:?\*\*:?",
        }

        for section, pattern in required_patterns.items():
            if not re.search(pattern, self.raw_content, re.IGNORECASE):
                errors.append(
                    f"Seção obrigatória '{section}' não encontrada no formato '- **{section}:**'."
                )

        return errors


class SessionNarrative(BaseModel):
    """Narrativa de retomada da sessão. Value-object dentro de SessionState.

    Cada campo mapeia para uma seção do corpo de `.harness/estado-da-sessao.md`.
    É escrita pelo agente; a CLI a carrega e a reinjeta, nunca a inventa.
    """

    feito: List[str] = Field(default_factory=list)
    proximos_passos: List[str] = Field(default_factory=list)
    pendencias: List[str] = Field(default_factory=list)
    ponteiros: List[str] = Field(default_factory=list)

    def is_empty(self) -> bool:
        return not (
            self.feito or self.proximos_passos or self.pendencias or self.ponteiros
        )


class SessionState(BaseModel):
    commit_hash: str
    active_feature: str
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    narrative: SessionNarrative = Field(default_factory=SessionNarrative)

    @field_validator("commit_hash")
    @classmethod
    def validate_commit_hash(cls, value: str) -> str:
        if not re.match(r"^[a-f0-9]{40}$", value):
            raise ValueError(
                f"Commit hash inválido: {value}. Deve ser um hash SHA1 de 40 caracteres."
            )
        return value

    def start_session(self, feature_name: str, commit_hash: str):
        self.active_feature = feature_name
        self.commit_hash = commit_hash
        self.start_time = datetime.now(timezone.utc)
        self.is_active = True

    def close_session(self, commit_hash: str):
        self.commit_hash = commit_hash
        self.is_active = False

    def update_active_feature(self, feature_name: str):
        if not self.is_active:
            raise ValueError("Não é possível atualizar uma sessão inativa.")
        self.active_feature = feature_name
