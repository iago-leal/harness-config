# Legacy Impact: Instalação do Harness por Prompt Estruturado

> Identificador: `003-instalacao-por-prompt`
> Data: `2026-06-23`

## 1. Mapeamento de Impacto no Legado

| Arquivo afetado | Componente (`_reversa_sdd/architecture.md`) | Tipo | Severidade | Justificativa |
| :--- | :--- | :--- | :--- | :--- |
| `harness-core/src/core/install/service.py` | Núcleo hexagonal — serviços de domínio | componente-novo | LOW | Novo `InstallPromptService`, isolado por `FileSystemPort`; não altera serviços existentes. |
| `harness-core/src/core/install/harness_profiles.py` | Núcleo hexagonal — serviços de domínio | componente-novo | LOW | Strategy de perfis por harness; sem dependência reversa de outros módulos. |
| `harness-core/src/core/install/template.md` | Núcleo hexagonal — recursos de serviço | componente-novo | LOW | Template de prompt co-localizado com o serviço, análogo ao `documentation/template.html`. |
| `harness-core/src/core/domain/config.py` | Domínio — configuração (`HarnessConfig`) | regra-alterada | LOW | O modelo `HarnessConfig`, antes ocioso, ganha um carregador `load_config`; passa a ter uso real. Nenhum campo alterado. |
| `harness-core/src/main.py` | Interface CLI (`main.py`) | regra-alterada | LOW | Novo subcomando `install-prompt` (parser + handler); os comandos existentes ficam intactos. |
| `harness-core/tests/test_install.py` | Suíte de testes | componente-novo | LOW | Cinco casos cobrindo o prompt por harness, escopo de projeto e sinalização do `SessionStart`. |

## 2. Diff Conceitual por Componente

### Núcleo (`core/install/`)
Introduz uma capacidade nova e coesa: gerar, por **introspecção** (mesmo padrão do `DocumentationService`), o prompt de instalação colável. O serviço compõe template estático + bloco de ganchos do perfil do harness ativo + superfície da CLI. Não há acoplamento a infraestrutura concreta além do `FileSystemPort` injetado.

### Domínio (`HarnessConfig`)
Fecha a dívida de "config decorativo" apontada em `_reversa_sdd/architecture.md#5-dividas-tecnicas-identificadas`: o `harness.toml` passa a ser lido como modelo tipado via `load_config`, e o `active_harness` finalmente alimenta comportamento (a escolha de perfil de ganchos).

### Interface CLI (`main.py`)
Ganha o subcomando `install-prompt`, que lê a config tipada e imprime o prompt no stdout. Aditivo: nenhum comando anterior muda de assinatura ou comportamento.

## 3. Regras Preservadas

Todas as regras 🟢 de `_reversa_sdd/domain.md` permanecem intactas:
* **RN-01..RN-02 (Sincronização/Resiliência):** não tocadas.
* **RN-03..RN-06 (Formatação/Blindagem/Opt-out):** não tocadas.
* **RN-07 (Âncora Git de Sessão):** não tocada.
* **RN-08..RN-09 (Documentação standalone/autossuficiente):** preservadas; o novo comando aparece automaticamente na introspecção do `doc-gen`.
* **RN-10 (Introspecção Dinâmica):** **reforçada** — o `InstallPromptService` reusa o mesmo princípio de derivar a saída da definição do `argparse`.

## 4. Regras Modificadas

Nenhuma regra de negócio 🟢 do legado foi alterada ou removida. A única mudança de comportamento de código é a ativação do `HarnessConfig` (antes ocioso), que não corresponde a uma regra de domínio do `domain.md`, e sim a uma redução de dívida técnica.
