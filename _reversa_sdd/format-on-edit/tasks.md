# Format-on-Edit (Formatting) — Tarefas de Implementação

> Regenerado pelo Writer em 2026-06-24 (Re-extração)
> Sequência executável para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

> ⚠️ Reescrita: a unit agora é o `FormattingService` Python (`harness-core`), não o script shell legado `hooks/format-on-edit.sh` (purgado). Sem `shfmt`, sem log, sem `systemMessage`.

## Pré-requisitos

- [ ] `ProcessPort` / `HostFormatterAdapter` disponíveis.
- [ ] `FileSystemPort` disponível.
- [ ] Formatadores de host instalados (`ruff`/`prettier`/`rustfmt`) — opcional (degrada a no-op).

## Tarefas

- [ ] T-01, Blindagem de diretórios pessoais (RN-04)
  - Origem no legado: `core/formatting/service.py`
  - Critério de pronto: caminho `~`, `~/Notas`, `~/.claude` aborta com retorno 0.
  - Confiança: 🟢

- [ ] T-02, Descoberta de raiz + opt-out (RN-N7/RN-06)
  - Origem no legado: `core/formatting/service.py`
  - Critério de pronto: sobe a árvore, aborta em `.no-autoformat`, marca raiz em `.git`/`harness.toml`, fallback `os.getcwd()`.
  - Confiança: 🟢

- [ ] T-03, Seleção do formatador por extensão (RN-N7)
  - Origem no legado: `core/formatting/service.py`
  - Critério de pronto: `.py`→ruff, `.js/.ts/.json/.css/.md`→prettier, `.rs`→rustfmt, demais → no-op.
  - Confiança: 🟢

- [ ] T-04, Precedência de executável local (RN-05)
  - Origem no legado: `core/formatting/service.py`
  - Critério de pronto: prioriza `.venv/bin/ruff`/`venv/bin/ruff`/`node_modules/.bin/prettier`; senão delega ao PATH.
  - Confiança: 🟢

- [ ] T-05, Não-bloqueio absoluto (RN-03)
  - Origem no legado: `core/formatting/service.py`
  - Critério de pronto: `try/except Exception` em todo o corpo; `format_file` sempre retorna 0.
  - Confiança: 🟢

- [ ] T-06, Adaptador de execução de formatador
  - Origem no legado: `adapters/process/formatter.py`
  - Critério de pronto: mapeia formatador→args; `FileNotFoundError`→`(127,...)`.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Happy path: arquivo `.py` em projeto com `harness.toml` dispara ruff e retorna 0.
- [ ] TT-02, Blindagem: arquivo em `~/Notas` não é formatado.
- [ ] TT-03, Resiliência: exceção/formatador ausente → retorna 0 sem bloquear.

## Ordem Sugerida

1. T-06 (adaptador) e T-01 (blindagem) primeiro.
2. T-02/T-03/T-04 (descoberta, seleção, precedência) compõem o corpo.
3. T-05 (não-bloqueio) envolve tudo.

## Lacunas Pendentes (🔴)

- Nenhuma 🔴. **T3** (autoformat por hook via stdin quebrava por `json` sem import) **resolvido** no commit `cf73980`. Resta a ressalva 🟡 **T4** (`[formatting]` inerte — blindagens/opt-out chumbados), ainda aberta.
