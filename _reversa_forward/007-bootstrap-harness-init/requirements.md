# Requirements: Script de Bootstrap Simples (harness-init)

> Identificador: `007-bootstrap-harness-init`
> Data: `2026-06-24`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Esta feature entrega a capacidade de inicializar e instalar o framework do harness em repositórios locais de destino diretamente via terminal do host, além de um mecanismo para atualizar essa instalação quando o núcleo evoluir. Ela expõe o subcomando `./harness init <destino>` a partir de uma instalação ativa do harness, que realiza a cópia completa do núcleo `harness-core`, do wrapper `harness` e da pasta `.harness/` para o destino, criando a venv e instalando os hooks locais. A feature também introduz o rastreamento do caminho de origem (`upstream_path`) para viabilizar avisos de nova versão e o comando `./harness upgrade` para atualização não destrutiva do núcleo local.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#5-dividas-tecnicas-e-bugs-latentes` | O harness-core é um módulo per-projeto autocontido de footprint global zero (MD-0005). | 🟢 |
| `_reversa_sdd/domain.md#27-bootstrap-de-ganchos-git` | `BootstrapService.install_hooks` realiza a instalação idempotente e não-bloqueante dos ganchos Git locais (`pre-commit` e `post-merge`). | 🟢 |
| `_reversa_sdd/inventory.md#wrapper-de-conveniencia-raiz-do-projeto` | O wrapper `harness` resolve a venv local em `harness-core/.venv/bin/python3` e repassa argumentos para `src/main.py`. | 🟢 |
| `_reversa_sdd/install/requirements.md#4-regras-de-negocio-novas-ou-alteradas` | A feature 003 de instalação por prompt delega para o agente a inicialização e ganchos locais através de colagem no chat. | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Desenvolvedor integrador | Inicializar o suporte a harness em um novo repositório de trabalho local. | Executa o subcomando `./harness init` passando o caminho do novo projeto; o script configura o core, a venv e os ganchos git automaticamente. |
| Desenvolvedor integrador | Atualizar a versão do core de um projeto local após evolução do repositório principal. | Executa `./harness upgrade` no projeto de destino e o núcleo local é atualizado mantendo as decisões intactas. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01: Inicialização via CLI do Upstream** 🟢
   - Origem no legado: `_reversa_sdd/domain.md#11-conceitos-e-entidades-chave` (módulo per-projeto)
   - Tipo: nova
   - Descrição: O comando de inicialização é um subcomando Python exposto no repositório de origem (`./harness init <caminho-destino>`). Se omitido, o destino padrão é a pasta de trabalho corrente (`pwd`). O diretório de destino deve ser um repositório git válido (conter a pasta `.git`).

2. **RN-02: Cópia física e isolamento per-projeto** 🟢
   - Origem no legado: `_reversa_sdd/domain.md#28-modulo-per-projeto-e-footprint-global-zero`
   - Tipo: nova
   - Descrição: O processo de inicialização copia fisicamente todo o conteúdo do diretório `harness-core/` (exceto `.venv` e arquivos de cache/build temporários) e o wrapper executável `harness` para a raiz do destino. Não são utilizados links simbólicos, garantindo o total desacoplamento e isolamento do destino.

3. **RN-03: Criação de venv e ganchos Git automatizada** 🟢
   - Origem no legado: `_reversa_sdd/bootstrap/requirements.md#regras-de-negocio`
   - Tipo: nova
   - Descrição: O script de inicialização deve criar o ambiente virtual Python (`.venv`) em `harness-core/` do destino e rodar `pip install` usando o `requirements.txt` copiado. Em caso de falha no host (falta do interpretador python ou internet), o script deve falhar barulhento com instruções legíveis. Concluída a venv, o script executa o bootstrap de ganchos Git (`pre-commit` e `post-merge`) no destino.

4. **RN-04: Metadados de Upstream e Atualização** 🟢
   - Tipo: nova
   - Descrição: O `init` grava em `.harness/setup.json` ou `harness.toml` do destino o parâmetro `upstream_path` apontando para o repositório original. O serviço de sincronização compara a versão do core local com o upstream. Se houver desatualização, emite um aviso no terminal/boot. O comando `./harness upgrade` no destino executa a cópia das atualizações sem alterar ou danificar as pastas de dados locais (`.harness/` e `.reversa/`).

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Subcomando de inicialização `init` | Must | `./harness init <destino>` copia o wrapper `harness`, a pasta `harness-core/` e inicializa o diretório `.harness/` no destino. | 🟢 |
| RF-02 | Validação de repositório Git de destino | Must | Aborta a execução se o diretório de destino não contiver a subpasta `.git`. | 🟢 |
| RF-03 | Configuração automática da `.venv` no destino | Must | Cria o ambiente virtual e instala as dependências em `harness-core/.venv` do destino. Falhas geram avisos explícitos e amigáveis. | 🟢 |
| RF-04 | Bootstrap automático de ganchos Git locais | Should | Executa o instalador de ganchos Git local (`pre-commit` e `post-merge`) no projeto de destino. | 🟢 |
| RF-05 | Persistência do caminho upstream no destino | Must | Grava o caminho absoluto do repositório de origem no `harness.toml` ou no setup do destino sob o campo `upstream_path`. | 🟢 |
| RF-06 | Verificação de versão e aviso de atualização | Should | Compara a versão local e a do upstream configurado, emitindo alertas se a versão local for mais antiga. | 🟢 |
| RF-07 | Subcomando `upgrade` não destrutivo | Must | Executa `./harness upgrade` a partir do projeto de destino, atualizando os binários do core e wrapper sem mexer nas decisões/sessão locais. | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Portabilidade | Compatibilidade total com sistemas baseados em Unix (macOS e Linux). | Wrappers e scripts executados em Bash e Python. | 🟢 |
| Robustez | Fail-fast legível no terminal do host para falhas do Python ou Git do host. | Evita falhas silenciosas na criação da venv ou cópia. | 🟢 |
| Idempotência | Reexecutar `harness init` ou `upgrade` não destrói ou duplica os ganchos git ou as decisões em `.harness/decisoes/`. | Respeito aos dados já gerados pelo usuário. | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Inicialização limpa de um novo projeto de destino
  Dado que executo `./harness init /tmp/projeto-destino` a partir do repositório original do harness
  E o diretório `/tmp/projeto-destino` é um repositório git válido
  Então a pasta `/tmp/projeto-destino/harness-core/` é criada com o código do core
  E o wrapper `/tmp/projeto-destino/harness` é copiado
  E a venv python é criada em `/tmp/projeto-destino/harness-core/.venv/` com dependências instaladas
  E os ganchos git são configurados em `/tmp/projeto-destino/.git/hooks/`
  E `.harness/setup.json` possui o campo `upstream_path` apontando para o repositório original do harness

Cenário: Atualização não destrutiva (Upgrade)
  Dado um repositório de destino já inicializado contendo a microdecisão `.harness/decisoes/MD-0001.md`
  Quando executo `./harness upgrade` dentro do repositório de destino
  Então os arquivos em `harness-core/` e o wrapper `harness` são atualizados a partir do upstream_path
  E a microdecisão `MD-0001.md` original é preservada perfeitamente intacta

Cenário: Alerta de versão desatualizada
  Dado que a versão do core local é `1.2.43` e a versão contida no upstream_path é `1.2.44`
  Quando executo qualquer comando local do harness (ou no boot do agente)
  Então um alerta legível informando que uma atualização está disponível é impresso no terminal
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | Permite disparar a inicialização do destino de forma direta. |
| RF-02 | Must | Segurança para evitar poluição em pastas que não são repositórios. |
| RF-03 | Must | venv e dependências são cruciais para que o núcleo funcione no destino. |
| RF-05 | Must | Essencial para viabilizar rastreamento e updates futuros. |
| RF-07 | Must | Viabiliza atualizações mantendo as decisões do usuário seguras. |
| RF-04 | Should | Automação dos hooks git no destino. |
| RF-06 | Should | Informa ativamente sobre novidades no core sem exigir consulta manual. |

## 9. Esclarecimentos

### Sessão 2026-06-24

- **Q:** Onde o comando `harness-init` deve residir e ser executado?
  **R:** Um subcomando Python na CLI existente (ex.: `./harness init <destino>`), rodando a partir do repositório central do harness onde o interpretador Python já está configurado. Isso mantém a lógica de bootstrap coesa no `harness-core`.
- **Q:** Como o `harness-core` deve ser disponibilizado no projeto de destino?
  **R:** Cópia física completa da pasta `harness-core/` (com exclusão de arquivos temporários e caches) para o projeto de destino, assegurando o isolamento absoluto per-projeto (footprint local completo) e eliminando dependências temporais ou espaciais de caminhos locais.
- **Q:** O script deve criar a venv e instalar as dependências no destino de forma automática?
  **R:** Sim, o comando tentará criar a `.venv` e rodar `pip install` automaticamente. Caso falte dependências de sistema no host ou conectividade, o processo aborta barulhento explicando os passos corretivos de forma legível.
- **Q:** Como o projeto de destino rastreia e atualiza seu Harness Core quando este evoluir?
  **R:** O processo de inicialização grava em configuração o parâmetro `upstream_path` apontando para o repositório de origem do harness. A sincronia do destino compara a versão local com a do upstream. Um novo comando `./harness upgrade` copia de forma limpa as atualizações do upstream para `harness-core/` e wrapper `harness`, preservando integralmente os dados do usuário em `.harness/` e `.reversa/`.

## 10. Lacunas

Nenhuma lacuna. Todas as dúvidas de arquitetura, isolamento e atualização foram sanadas na rodada de esclarecimentos do dia 2026-06-24.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-24 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-06-24 | Dúvidas de interface, cópia per-projeto, venv e ciclo de vida de atualização resolvidas por `/reversa-clarify` | reversa |
