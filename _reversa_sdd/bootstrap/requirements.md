# Bootstrap e Evolução (Ganchos Git, Init e Upgrade) — Requisitos (Requirements)

> Regenerado pelo Writer em 2026-06-24 (Re-extração pós-feature 007)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`.harness/harness-core/src/core/bootstrap/service.py`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/core/bootstrap/service.py) e [`.harness/harness-core/src/core/bootstrap/init_service.py`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/core/bootstrap/init_service.py). Drivers: `src/main.py` (subcomandos `bootstrap`, `init` e `upgrade`).
> **Reconciliação de 2026-08-11-b (feature 028, não commitada nesta data):** o `init` ganhou um último passo, `_ensure_decisions_guidance(target_path, active_harness)` — grava no arquivo da engine ativa (claude→`CLAUDE.md`, antigravity→`AGENTS.md`, gemini→`GEMINI.md`) o trecho de guidance que ensina o agente a consultar microdecisões sob demanda (visão compacta → índice → fichas). Idempotente pelo marcador `<!-- harness:decisoes -->` (presente → não regrava; ausente → append; arquivo inexistente → cria) e **write-once**: o `upgrade` jamais o toca (risco aceito: guidance defasado em instalações antigas até intervenção manual). RN-N58; ver `domain.md#2.26`, ADR 0028 / MD-0022.

## Visão Geral

Gerencia a inicialização física (`init`), instalação de ganchos locais Git (`bootstrap`) e atualização evolucionária (`upgrade`) do framework em diretórios locais de destino de forma isolada, resiliente a falhas e não destrutiva.

## Responsabilidades

- Criar `.git/hooks/` (se ausente) e gravar os scripts `pre-commit` e `post-merge` de forma idempotente e não bloqueante. 🟢
- Inicializar novos workspaces em diretórios locais copiando os arquivos necessários e provisionando a `.venv` e ganchos com tratamento fail-fast no host. 🟢
- Atualizar o wrapper e os arquivos do core a partir do upstream de forma não destrutiva, preservando intactos todos os metadados locais de decisões e análises. 🟢
- Registrar o link do upstream e a versão física corrente no `harness.toml`. 🟢

## Regras de Negócio

- **RN-N15 — Bootstrap idempotente e não-bloqueante:** `install_hooks` grava `pre-commit` (→ `format`) e `post-merge` (→ `decisions`) reescrevendo a cada execução; cada script só roda se o interpretador (`$PYTHON_CLI`) existir, senão `exit 0`. 🟢
- **RN-N18 — Configuração de Upstream e Versão:** O `harness.toml` no destino armazena de forma persistente a versão física instalada (`version`) e o caminho absoluto do core de origem (`upstream_path`) na seção `[harness]`. 🟢
- **RN-N19 — Inicialização de Repositório Alvo:** A inicialização copia fisicamente o core e wrapper, ignorando arquivos de cache e build local (`.git`, `.venv`, etc.), configura o ambiente virtual local e instala ganchos locais, abortando com alertas verbosos de setup fail-fast caso falte dependências no host. 🟢
- **RN-N20 — Evolução Não-Destrutiva:** O upgrade atualiza wrapper e código do core Python a partir do upstream configurado, mas preserva obrigatoriamente intactas as pastas `.reversa/` (dados de engenharia reversa) e `.harness/decisoes/` (metadados arquiteturais). 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Instalar `pre-commit` e `post-merge`. | Must | Após `./harness bootstrap`, os dois scripts existem em `.git/hooks/` e invocam a CLI (`format`/`decisions`). |
| RF-02 | Idempotência. | Must | Reexecutar o bootstrap regrava os scripts sem erro nem duplicação. |
| RF-03 | Não-bloqueio sob interpretador ausente. | Must | Se o interpretador não existir, o gancho faz `exit 0` sem abortar o commit/merge. |
| RF-04 | Inicializar Repositório Alvo (`init`). | Must | `./harness init <destino>` cria o destino, copia recursivamente os arquivos relevantes filtrando lixo local, provisiona a `.venv` local e instala ganchos Git. Falha com erro instrutivo claro se a dependência do python3/venv faltar no host. |
| RF-05 | Atualização do Core (`upgrade`). | Must | `./harness upgrade` localiza o core original via `upstream_path`, atualiza o wrapper e arquivos de código no destino, mas garante a integridade preservando intactas as pastas `.reversa/` e `.harness/decisoes/`. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Robustez | Não bloqueia operações Git se o ambiente estiver incompleto. | `core/bootstrap/service.py` (`exit 0` condicional) | 🟢 |
| Reprodutibilidade | Scripts e códigos copiados deterministicamente a cada execução. | `core/bootstrap/init_service.py` | 🟢 |
| Isolamento | Localidade estrita per-projeto (footprint zero global). | `core/bootstrap/init_service.py` (criação de venv local e cópia física sem links) | 🟢 |

## Critérios de Aceitação

```gherkin
Dado um repositório sem ganchos instalados
Quando executo `./harness bootstrap`
Então `.git/hooks/pre-commit` e `.git/hooks/post-merge` são criados e invocam a CLI (format/decisions).

Dado que a venv do harness-core não existe
Quando um commit dispara o pre-commit instalado
Então o gancho faz exit 0 sem bloquear o commit.

Dado um repositório vazio de destino
Quando executo `./harness init <destino>`
Então os arquivos do core e o wrapper são copiados, a venv local é provisionada e os ganchos git são instalados.

Dado uma instalação física em um destino
Quando executo `./harness upgrade`
Então os arquivos de código e wrapper são atualizados com os novos arquivos do upstream, mas as pastas .reversa/ e .harness/decisoes/ locais continuam intocadas.
```

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `core/bootstrap/service.py` | `BootstrapService.install_hooks` | 🟢 |
| `core/bootstrap/init_service.py` | `InitService.init_target`, `InitService.upgrade_target` | 🟢 |
| `src/main.py` | Subcomandos `bootstrap`, `init`, `upgrade` | 🟢 |
