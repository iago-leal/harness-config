# Investigation: harness-core como módulo per-projeto autocontido

> Identificador: `006-harness-core-config-canonica`
> Data: `2026-06-24`

## 1. Pesquisa de fundo

A feature nasceu da intenção registrada em `.harness/decisoes/MD-0004.md` ("tornar o harness-core a referência canônica única, substituto da config global") e do RF-04 diferido da feature 005. A clarify de 2026-06-24 reviu a premissa: em vez de substituir o `~/.claude` (alvo do fornecedor, com raio de explosão global), a feature consolida o harness-core como **módulo per-projeto autocontido**. Esta investigação foca nas três frentes técnicas que sobraram: a parametrização do caminho de sessão, a unificação da via de configuração e o contrato de footprint.

## 2. Achados do código vivo (pós-`cf73980`)

- `harness-core/src/core/domain/config.py`: `HarnessConfig` tem `harness`, `formatting`, `sync`, `decisions`. **Não** há `session`. `DecisionsSection` é o molde direto (três campos com defaults `.harness/...`).
- `harness-core/src/main.py`: `load_harness_config` (dict legado, linhas 22-42) é usado **só** em `main.py:143`; seu único leitor real é o branch `cmd`, que faz `config["harness"]["active_harness"]` na linha 214. O caminho de sessão está chumbado na linha 193. Os branches `decisions` e `install-prompt` já usam `load_config`.
- `harness-core/src/adapters/mcp/server.py`: `session_command` chumba o caminho na linha 93. `process_decisions` já usa `load_config` (linha 61). Os bugs T1/T2/T3 da extração já estão corrigidos no código vivo.
- `harness-core/src/core/ports/fs.py`: `FileSystemPort` expõe `read_file`, `write_file`, `write_file_atomic`, `exists`, `list_dir`, `makedirs`, `remove`. **Toda** escrita do harness passa por essa porta — é o que torna o contrato de footprint viável por um duplo de teste.
- `harness-core/tests/`: 16 arquivos, com `helpers.py` (local natural do duplo), `test_domain.py` (config), `test_cli.py` (cmd/sessão) e `test_mcp.py`.

## 3. Alternativas avaliadas

### 3.1 Parametrizar o caminho de sessão
- **Escolhida:** seção `[session]` no `harness.toml` + `SessionSection` no loader, lida por CLI e MCP. Espelha `[decisions]` (ADR 0012), fonte única, fecha T2.
- Descartada: manter o literal chumbado nos dois sites — é justamente o drift que originou T2.
- Descartada: uma seção genérica `[paths]` agregando todos os caminhos — foge do precedente e mistura concerns.

### 3.2 Unificar a via de configuração (T5)
- **Escolhida:** remover `load_harness_config`, ler tudo por `load_config` tipada. O único consumidor (`cmd` → `active_harness`) migra para `config.harness.active_harness`.
- Descartada: manter as duas vias — é a dívida T5 documentada em `_reversa_sdd/gaps.md#g-09`.

### 3.3 Contrato de footprint (RF-03) — a frente mais nova
- **Escolhida:** teste com duplo `RecordingFileSystem` que implementa `FileSystemPort`, captura todas as escritas e afirma que cada caminho resolve dentro da raiz do repo de teste, nunca sob `~/.claude` ou `~/.agent-memory`. Barato, determinístico, aproveita a arquitetura hexagonal.
- Descartada: **guard de runtime** no `LocalFileSystemAdapter` que recuse escritas fora de uma raiz permitida. Atraente pelo "erro barulhento", mas arriscado: quebraria escritas legítimas (`harness-docs.html` gerado no cwd, alvos de `format` passados pelo usuário) e é mudança de comportamento de produção que o requisito não pediu. Fica como possível endurecimento futuro, não nesta feature.
- Descartada: teste de integração rodando o CLI real e varrendo o filesystem — mais lento e instável, sem ganho sobre o duplo.

## 4. Padrões aplicáveis

- **Caminhos por configuração** (ADR 0012, `_reversa_sdd/adrs/0012-...`): config tipada lida por `load_config`, injetada na borda; o domínio recebe o caminho por parâmetro. `[session]` é a aplicação direta.
- **Test double / Spy** sobre porta hexagonal: o `RecordingFileSystem` é um Spy que verifica interações (caminhos de escrita), não estado — adequado a um contrato de invariante.
- **Falha barulhenta** (`get_sink`/`get_profile` levantam `ValueError`): o contrato de footprint segue a mesma filosofia, falhando alto em vez de degradar em silêncio.

## 5. Itens adjacentes deixados fora (visibilidade, sem ação)

- G-10: MCP `process_decisions` deriva `header_file` por `os.path.join(decisoes_dir, "_cabecalho.md")` (`server.py:65`), ignorando `config.decisions.header_file`. Inconsistência real, fora do escopo da 006.
- T4: `FormattingSection` (`exclude_paths`, `opt_out_file`) declarada no `harness.toml` mas ignorada pelo serviço (blindagens chumbadas). Fora do escopo.
- Sem lock file / CI (`_reversa_sdd/dependencies.md`): dívida de reprodutibilidade pré-existente, não tratada aqui.
