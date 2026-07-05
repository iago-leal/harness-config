# ADR 0020: Fonte única de execução (shim + upstream) para `init`, com `harness migrate` para converter a base já instalada

- **Status:** Aceito (parcial — ver Consequências/em aberto: a aposentadoria de `upgrade`/`sync` prevista originalmente foi desescopada)
- **Data:** 2026-07-01 (feature 020-fonte-unica-e-hooks)
- **Contexto Técnico:** Novo `src/core/bootstrap/shim.py` (`render_shim()`); `InitializationService.initialize_project` reescrito para não copiar core nem criar `.venv`; novo `src/core/migrate/service.py` (`MigrateService`); novo método `remove_tree` em `FileSystemPort` (+ adapter local + fakes); `src/core/install/claude_settings.py` com merge por-item; `BootstrapService.install_hooks` não-destrutivo por assinatura; `CORE_VERSION` derivado de `HarnessSection().version` (bump `1.3.0 → 2.0.0`). `upgrade_project`, `SyncService` e o alerta passivo de versão **permanecem no código**, ao contrário do plano original (ver Consequências).
- **Escala de Confiança:** 🟢 CONFIRMADO para os itens implementados (código as-built; suíte 238 no fechamento da feature; smoke real de `migrate --dry-run` em sandbox). 🟡 para o estado do desescopo (registrado em `actions.md`, não re-verificado linha a linha nesta reconciliação).
- **Decisões relacionadas:** ADR 0013 (harness-core módulo per-projeto, footprint zero — premissa revisada aqui); ADR 0016 (materialização única `init`/`upgrade`, padrão de merge por named-hook que esta ADR estende ao `.claude/settings.json`); ADR 0014 (bootstrap e evolução do tooling); domain.md §2.17 (RN-N36..N40) e a nota de reconciliação no topo do arquivo.

## Contexto e Problema

Cada `harness init` replicava fisicamente o `harness-core` inteiro e criava uma `.venv` própria no destino. Medição real em `~/dev` (2026-07-01): **17 instalações, ~1,83 GB no total, dos quais ~97% eram venvs duplicadas** (o código-fonte replicado somava só ~3 MB por projeto) — duplicação de disco sem ganho correspondente, já que todos os projetos rodam na mesma máquina e sempre têm o upstream acessível. Paralelamente, dois materializadores eram **destrutivos**: o merge de hooks do Claude em `.claude/settings.json` substituía o array inteiro de cada evento (apagando hooks próprios do usuário no mesmo evento), e `install_hooks` sobrescrevia `pre-commit`/`post-merge` incondicionalmente (descartando hooks git alheios).

## Decisão

**Fonte única de execução para instalações novas, conversão explícita para as existentes.** Duas peças centrais:

1. **`init` fonte única.** `initialize_project` deixa de copiar o `harness-core` e de criar `.venv` no destino. Grava o **shim** (`render_shim()`) no lugar do wrapper — resolve `upstream_path` do `harness.toml` do próprio projeto, `cd` para a raiz e executa o Python/`main.py` do **upstream**, repassando `$@`/exit code; erro barulhento se o upstream estiver ausente. A viabilidade repousa num fato auditado no legado (RF-08): todo o core já resolve dados do projeto pelo `cwd` (`os.getcwd()`, `load_config` relativo); os únicos usos de `__file__` apontam para assets do próprio core (templates, `sys.path`) — que corretamente devem vir do upstream. Apontar o shim para o upstream não exige tocar o core. O footprint de **escrita** per-projeto (ADR 0013) é preservado: só a leitura de código passa a cruzar a fronteira do repositório; toda escrita de estado (sessão, decisões, índice) continua sob `.harness/` do projeto-alvo.
2. **`harness migrate` para a base já instalada.** `MigrateService.migrate(root, dry_run, upstream_self)` varre uma raiz por projetos com `harness.toml` e converte cada um do layout copiado para a fonte única, na ordem shim → ganchos → settings → remoção de `version` → remoção da cópia do core **por último** (nunca deixa o projeto sem executor). Guardas: nunca migra o próprio upstream nem uma autorreferência circular; exige o core do upstream presente; `_safe_remove_core` (usa o novo `FileSystemPort.remove_tree`) recusa remover qualquer diretório cujo nome-base não seja `harness-core`. Suporta `--dry-run`. É a **exceção consciente** ao footprint per-projeto (ADR 0013): atua sobre outros projetos por design, como ferramenta de manutenção da base, não como operação isolada.

Junto, dois materializadores passam a ser **não-destrutivos**: o merge do `.claude/settings.json` passa a ser por-item dentro do array de cada evento (identifica pela assinatura no `command`, substitui/insere, preserva o resto); `install_hooks` passa a identificar hooks do harness por assinatura e preservar hooks alheios sem ela (encadeando-os). Ambos passam a invocar o shim em vez do python local.

## Alternativas Consideradas

- **Symlink em vez de shim executável:** descartado — menos portável entre filesystems/OS, e não permite injetar tratamento de erro amigável quando o upstream está ausente (um symlink quebrado falha com uma mensagem genérica do shell).
- **Migração automática no primeiro boot pós-upgrade:** descartado — mudar o layout de um projeto sem ação explícita do mantenedor é arriscado (remove diretórios); o `--dry-run` e a natureza opt-in do `migrate` foram preferidos.
- **Remover `upgrade`/`sync`/`version` já nesta feature (plano original, D-05 do roadmap):** **desescopado em 2026-07-01**, não descartado por mérito técnico — ver Consequências.

## Consequências

- **Positivas:**
  - Instalações novas não duplicam mais ~108 MB de venv por projeto; o código-fonte do core passa a ter um único ponto de verdade em execução (o upstream).
  - Hooks git e `settings.json` do Claude deixam de ser pontos de perda silenciosa de configuração alheia.
  - `harness migrate` dá ao mantenedor uma rota explícita, auditável (`--dry-run`) e segura (guardas contra autodestruição) para recuperar o espaço das 17 instalações existentes, sem pressa.
- **Negativas / em aberto:**
  - **O plano original também previa tornar `upgrade` um no-op e remover `SyncService`/o alerta passivo de versão/o campo `version`** (roadmap D-05, actions T008/T009/T013/T015/T016). A varredura de implementação revelou que `SyncService` e `upgrade_project` sustentam a `UpgradeOffer` do encerramento de sessão (feature 014, `session/offers.py`) — removê-los quebraria parte do fluxo de fechamento (features 013-019), escopo maior e mais sensível que o previsto. **O mantenedor decidiu adiar essa descontinuação para uma feature futura** (a candidata seria a "021", mas esse número foi ocupado por uma feature diferente — o resume ancorado — então a descontinuação de `sync`/`upgrade`/oferta-014 é uma feature **ainda não numerada**, 022 ou posterior). Até lá, `upgrade` continua recopiando o core fisicamente para instalações no layout antigo, coexistindo com `migrate`; `layout.py` mantém os caminhos-candidato legados (`CORE_CONFIG_CANDIDATE_RELPATHS`) que a limpeza removeria.
  - `harness migrate` **não foi executado** nos 17 projetos reais até esta reconciliação — é ação separada e deliberada do mantenedor, não disparada automaticamente por nenhuma feature.
  - Sob fonte única, todos os projetos convertidos passam a seguir a HEAD única do upstream — trade-off aceito explicitamente (travado via PCCP): não há mais isolamento de versão por projeto.
