# Investigation: Reprodutibilidade e Configuração Viva de Formatação

> Identificador: `008-reprodutibilidade-e-config`
> Data: `2026-06-24`

## 1. Gerenciamento de Dependências com `uv`

Para garantir um build estável e determinístico sem alterar a natureza minimalista do projeto, analisamos o uso da ferramenta `uv`.

### Abordagem Escolhida: `uv pip compile`

O `uv` oferece compatibilidade direta com arquivos `requirements.txt` clássicos, permitindo compilar e fixar dependências transitivas de forma determinística:

1. Mantemos um arquivo fonte de dependências `requirements.in` contendo as dependências de alto nível com especificações flexíveis:
   ```text
   toml>=0.10.2
   pydantic>=2.0.0
   fastmcp>=0.4.1
   pytest>=8.0.0
   ```
2. Compilamos esse arquivo para gerar um `requirements.txt` travado com todas as sub-dependências resolvidas de forma estrita:
   ```bash
   uv pip compile requirements.in -o requirements.txt
   ```
3. O build de CI e do setup de desenvolvimento utilizará o `requirements.txt` gerado, garantindo a reprodutibilidade absoluta (lock implícito).

---

## 2. Injeção de Configuração no `FormattingService`

Atualmente, o `FormattingService` é instanciado em `main.py` e `server.py` sem conhecimento de configuração:
```python
service = FormattingService(fs, process)
```

### Abordagem Escolhida: Injeção do `HarnessConfig`

Injetaremos o objeto de configuração `HarnessConfig` no construtor do `FormattingService`:
```python
class FormattingService:
    def __init__(self, fs: FileSystemPort, process: ProcessPort, config: Optional[HarnessConfig] = None):
        self.fs = fs
        self.process = process
        self.config = config or HarnessConfig() # Fallback para defaults
```

---

## 3. Validação de Exclusões e Opt-out Dinâmico

### 3.1 Resolvendo o arquivo de opt-out configurado
No loop de subida recursiva da árvore de diretórios do `FormattingService`, em vez do valor rígido `.no-autoformat`, leremos o nome do arquivo dinamicamente:
```python
opt_out_filename = self.config.formatting.opt_out_file
opt_out_file = os.path.join(current, opt_out_filename)
if self.fs.exists(opt_out_file):
    return 0
```

### 3.2 Casando caminhos de exclusão (`exclude_paths`)
O `harness.toml` define `exclude_paths` como uma lista de strings. Como o usuário selecionou o comportamento de casar glob patterns e prefixos simples:
1. Normalizamos o caminho do arquivo para ser relativo à raiz do projeto.
2. Varremos os padrões contidos em `self.config.formatting.exclude_paths`.
3. Para cada padrão:
   - Se for um padrão contendo caracteres curingas (`*`, `?`, `[`), utilizamos `fnmatch.fnmatch` para validar.
   - Caso contrário, realizamos uma checagem de prefixo simples (ex: se o caminho relativo começa com o padrão) ou correspondência exata.
4. Se houver correspondência, abortamos com retorno `0`.

Exemplo de implementação conceitual em Python:
```python
import fnmatch

def should_exclude(self, abs_file_path: str, project_root: str) -> bool:
    # 1. Blindagens de segurança fixas do sistema continuam valendo incondicionalmente
    home = os.path.expanduser("~")
    if abs_file_path == home or abs_file_path.startswith(os.path.join(home, "Notas")) or abs_file_path.startswith(os.path.join(home, ".claude")):
        return True
        
    # 2. Exclusões dinâmicas do TOML
    rel_path = os.path.relpath(abs_file_path, project_root)
    
    for pattern in self.config.formatting.exclude_paths:
        # Normalização do padrão
        pattern = pattern.strip()
        # Se contiver curingas, usa fnmatch
        if any(char in pattern for char in ("*", "?", "[", "]")):
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(abs_file_path), pattern):
                return True
        else:
            # Checagem de prefixo (diretório) ou correspondência exata
            if rel_path.startswith(pattern) or rel_path == pattern:
                return True
                
    return False
```

---

## 4. Estrutura de CI/CD (GitHub Actions)

Configuraremos um workflow simples em `.github/workflows/ci.yml` para rodar a suíte pytest no ambiente do repositório:
- **Gatilho:** Commit em qualquer branch ou Pull Request para `main`.
- **Ambiente:** `ubuntu-latest`.
- **Passos:**
  1. Checkout do repositório.
  2. Instalar o `uv` (usando o setup action oficial `astral-sh/setup-uv`).
  3. Instalar o Python.
  4. Executar os testes via pytest em `harness-core` (`PYTHONPATH=. uv run pytest`).
  
Isso garantirá a validação automática rápida de integridade do código sem custos de infraestrutura adicionais.
