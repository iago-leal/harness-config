# ADR 0014: Mecanismo de Bootstrap e Evolução do Tooling (init/upgrade)

- **Status:** Aceito
- **Data:** feature 007 — commit `1b23498`
- **Contexto Técnico:** Módulo `core/bootstrap/init_service.py` (`InitService`), CLI `main.py` (comandos `init` e `upgrade`), `core/domain/config.py` (campos `upstream_path` e `version` na seção `[harness]`), `core/sync/service.py` (método `check_version_update`), `tests/test_init.py`
- **Escala de Confiança:** 🟢 CONFIRMADO
- **Decisões relacionadas:** MD-0005, ADR 0013; watch items **W001-W003** da feature 007

## Contexto e Problema

Com o `harness-core` consolidado como módulo per-projeto autocontido de footprint global zero (ADR 0013), surgiu a necessidade de simplificar a instalação inicial (bootstrapping) em novos repositórios locais do desenvolvedor e o processo de evolução (atualização) de sua infraestrutura física.

Anteriormente, para usar o Harness em um repositório novo, o usuário precisaria realizar cópias de código manuais e setups de ambiente virtual. Além disso, atualizar o core local com melhorias implementadas no repositório de desenvolvimento (upstream) dependia de intervenções manuais propensas a erros, sob risco de sobrescrever arquivos de dados preciosos locais de engenharia reversa (como a pasta `.reversa/` e as fichas `.harness/decisoes/`).

## Decisão

Implementar mecanismos nativos de bootstrap (`init`) e upgrade evolucionário (`upgrade`) no wrapper `./harness` e CLI `main.py`:

1. **Inicialização Física (`init <destino> [--harness {claude,gemini,antigravity}]`):** realiza a cópia recursiva e idempotente de todo o `.harness/harness-core/` e do wrapper `harness` de raiz para o diretório de destino. Descarta e ignora arquivos de cache e controle de versão locais do upstream (`.git/`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `tmp/`). Configura a `.venv` no destino via `ProcessPort.run_command` de forma fail-fast com alertas human-actionable se faltarem dependências no host. Configura o `harness.toml` padrão do destino e instala ganchos Git locais automaticamente.
2. **Associação ao Upstream (`upstream_path` e `version`):** O `harness.toml` do repositório de destino passa a conter a versão instalada (`version`) e o caminho físico absoluto do repositório upstream original (`upstream_path`), permitindo checagem passiva e upgrade direto.
3. **Evolução Não-Destrutiva (`upgrade`):** atualiza fisicamente o wrapper e o código do core no destino a partir do upstream, mas garante a integridade preservando intactas as pastas locais de dados `.reversa/` e de decisões arquiteturais `.harness/decisoes/`.
4. **Checagem Passiva de Versões:** CLI e MCP realizam leitura passiva no boot comparando a versão local com a versão do upstream. Se o upstream possuir versão maior, exibem alertas de upgrade discretos, sem usar rede ou subprocessos bloqueantes (operação puramente de I/O local via `FileSystemPort`), mantendo a resiliência offline e a performance do boot.

## Alternativas Consideradas

- **Utilizar symlinks entre repositórios:** rejeitada — reintroduziria acoplamento temporal e espacial entre projetos locais no host, violando a premissa de isolamento físico estrito de cada repositório e o footprint global zero (ADR 0013).
- **Consultar repositório Git remoto ou registro npm no boot:** descartada — violaria a resiliência offline do Harness e adicionaria latências pesadas de rede no tempo de boot da CLI e do servidor MCP.
- **Limpeza completa do diretório core no upgrade:** rejeitada — acarretaria perda de arquivos locais adicionados pelo usuário no core, ganchos customizados ou microdecisões. A atualização deve ser cirúrgica e preservadora de dados.

## Consequências

- **Positivas:**
  - Instalação e provisionamento de novos repositórios locais simplificados em um único comando de terminal.
  - Atualização evolucionária segura e automatizada (não destrutiva).
  - Alertas passivos e eficientes de atualização no boot sem ônus de latência.
- **Negativas:**
  - A duplicação física do core nos repositórios do host consome maior espaço em disco (footprint físico) do que abordagens baseadas em symlinks ou referências globais.
