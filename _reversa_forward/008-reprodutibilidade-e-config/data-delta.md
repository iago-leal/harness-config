# Delta no Modelo de Dados: Reprodutibilidade e Configuração Viva de Formatação

> Identificador: `008-reprodutibilidade-e-config`
> Data: `2026-06-24`

## 1. Alterações no Esquema de Configuração (`harness.toml`)

Não há adição, remoção ou modificação de campos na estrutura de dados do arquivo `harness.toml`. O modelo `HarnessConfig` já possui suporte tipado para as seções de formatação na classe `FormattingSection` em `src/core/domain/config.py`:

```python
class FormattingSection(BaseModel):
    exclude_paths: List[str] = Field(default_factory=list)
    opt_out_file: str = ".no-autoformat"
```

O delta reside inteiramente na **ativação funcional** dessas configurações na camada de lógica de negócios do `FormattingService`, eliminando a discrepância onde alterações no `harness.toml` eram ignoradas pelo sistema.

---

## 2. Diferenças e Mapeamento de Estado

### Estado Anterior (Ignorado)
```toml
[formatting]
exclude_paths = ["tmp/"]
opt_out_file = ".no-autoformat"
```
* **No código:** `exclude_paths` era ignorado; opt-out de formatação procurava estritamente pelo literal chumbado `".no-autoformat"`.

### Estado Novo (Consumido Dinamicamente)
* **No código:** `FormattingService` consome `config.formatting.exclude_paths` (validando os caminhos por glob pattern e prefixo) e procura pelo arquivo cujo nome é configurado em `config.formatting.opt_out_file` para interromper a formatação.

---

## 3. Plano de Migração de Dados

Como não há alteração de esquema nem persistência em banco de dados:
* **Ação:** Nenhuma migração de dados é necessária. Os arquivos `harness.toml` existentes continuarão funcionando imediatamente sem necessidade de alteração ou reconfiguração.
