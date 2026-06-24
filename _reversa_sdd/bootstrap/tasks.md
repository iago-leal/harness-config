# Bootstrap e Evolução — Tarefas de Implementação

> Regenerado pelo Writer em 2026-06-24 (Re-extração pós-feature 007)
> Sequência executável para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

## Pré-requisitos

- [ ] `FileSystemPort` disponível (criação, cópia, exclusão, gravação de diretórios).
- [ ] `ProcessPort` disponível (execução de comandos no host).
- [ ] Permissões de escrita nos caminhos de destino.

## Tarefas

- [ ] T-01, Implementar `_pre_commit_script` e `_post_merge_script`
  - Origem no legado: `core/bootstrap/service.py`
  - Critério de pronto: retornam corpos Bash que invocam a CLI com `format`/`decisions` e fazem `exit 0` se o interpretador não existir.
  - Confiança: 🟢

- [ ] T-02, Implementar `install_hooks(repo_path)`
  - Origem no legado: `core/bootstrap/service.py`
  - Critério de pronto: cria `.git/hooks/`, grava os dois scripts de forma idempotente e retorna os caminhos.
  - Confiança: 🟢

- [ ] T-03, Expor o subcomando `bootstrap` na CLI
  - Origem no legado: `src/main.py`
  - Critério de pronto: `./harness bootstrap` instala os ganchos no repositório corrente.
  - Confiança: 🟢

- [ ] T-04, Criar serviço de bootstrap físico (`InitService.init_target`)
  - Origem no legado: `core/bootstrap/init_service.py`
  - Critério de pronto: Copia recursivamente os arquivos, ignora pastas de desenvolvimento local (`.git`, `.venv`), persiste o `harness.toml` inicial, cria o ambiente virtual `.venv` no destino e instala ganchos Git.
  - Confiança: 🟢

- [ ] T-05, Criar serviço de atualização não-destrutiva (`InitService.upgrade_target`)
  - Origem no legado: `core/bootstrap/init_service.py`
  - Critério de pronto: Atualiza wrapper e código de core a partir do upstream, preservando intactas as pastas locais `.reversa/` e `.harness/decisoes/`.
  - Confiança: 🟢

- [ ] T-06, Expor os subcomandos `init` e `upgrade` na CLI e adicionar a checagem passiva de atualização
  - Origem no legado: `src/main.py` e `core/sync/service.py`
  - Critério de pronto: `./harness init` e `./harness upgrade` integrados no argparse e alertas discretos de versão desatualizada exibidos no boot sem latências de rede.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Happy path do bootstrap: após `install_hooks`, os dois scripts existem e referenciam a CLI.
- [ ] TT-02, Idempotência do bootstrap: reexecutar regrava os scripts sem erros.
- [ ] TT-03, Sucesso da inicialização (`init_target`): `./harness init` cria o diretório de destino, copia o core, configura `upstream_path` e versão no `harness.toml`, provisiona `.venv` e ganchos.
- [ ] TT-04, Sucesso do upgrade (`upgrade_target`): `./harness upgrade` copia novos arquivos de core do upstream, mas mantém intocados os diretórios de dados locais `.reversa/` e `.harness/decisoes/` do destino.
- [ ] TT-05, Falha-rápida do init: O init captura erros do host na criação da `.venv` (CalledProcessError) e gera logs human-actionable com caminhos para resolução.

## Ordem Sugerida

1. T-01 e T-02 (bootstrap) antes de T-03 (subcomando bootstrap CLI).
2. T-04 e T-05 (init/upgrade) antes de T-06 (subcomandos init/upgrade CLI + versão).
3. TT-03 a TT-05 na validação de testes de inicialização.

## Lacunas Pendentes (🔴)

- Nenhuma 🔴.
