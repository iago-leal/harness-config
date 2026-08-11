# Data Delta: Exportador kanban derivado da Medicao

> Identificador: `027-exportador-kanban`
> Data: `2026-08-11`

## 1. Modelos transitórios (pydantic, `core/progress/service.py`)

Novos modelos (as-built 2026-08-11):

```python
class Demanda(BaseModel):
    """Card manual do board em coluna não-done: fila de entrada do mantenedor."""
    card_id: str = ""
    titulo: str = ""
    coluna: str = ""  # todo | in-progress | testing

class AcaoProgresso(BaseModel):
    """Uma ação individual do actions.md, com o ID real da tabela (T00N)."""
    acao_id: str
    descricao: str = ""
    fase: str = ""
    feita: bool = False
    criada_em: str = ""  # 1º ts da ação no progress.jsonl; fallback started-at
```

O `AcaoProgresso` não estava no plano original: entrou porque a `Medicao` só
carregava agregados por fase, e ids ordinais (`#1`, `#2`) seriam instáveis a
reordenação da tabela — os cards exigem o ID real. `stages.py` ganhou o
extrator `listar_acoes`.

`FeatureProgresso` ganha `iniciada_em: str` e `acoes: List[AcaoProgresso]`;
`Medicao` ganha:

```python
board_habilitado: bool = False
demandas: List[Demanda] = Field(default_factory=list)
```

Nada disso é persistido pelo harness: a `Medicao` segue transitória.

## 2. Configuração (`core/domain/config.py`)

```python
class ProgressKanbanSection(BaseModel):
    enabled: bool = False
    file: str = ".vscode/vscode-kanban.json"

class ProgressSection(BaseModel):
    file: str = ".harness/progresso.md"
    kanban: ProgressKanbanSection = Field(default_factory=ProgressKanbanSection)
```

Toml correspondente (opt-in por projeto):

```toml
[progress.kanban]
enabled = true
# file = ".vscode/vscode-kanban.json"  # default
```

Herança sem migração: toml sem a seção comporta-se exatamente como hoje.

## 3. Artefato derivado novo (board)

`.vscode/vscode-kanban.json` — objeto com chaves `todo`, `in-progress`, `testing`, `done` (arrays de cards). Estrutura de card e regras de posse/merge no contrato `interfaces/kanban-board.md`. Versionado no git (D3 do clarify).

## 4. Migrações

Nenhuma: sem banco, sem mudança de schema persistido, default desligado.
