# ADR 0013: harness-core como módulo per-projeto autocontido com footprint global zero

- **Status:** Aceito
- **Data:** feature 006 — commit `e894c59`
- **Contexto Técnico:** Módulo `core/domain/config.py` (`SessionSection`), drivers `main.py` e `adapters/mcp/server.py`, `harness.toml` (seção `[session]`), `tests/test_footprint.py` + `tests/helpers.py` (`RecordingFileSystem`)
- **Escala de Confiança:** 🟢 CONFIRMADO
- **Decisões relacionadas:** MD-0005 (refina MD-0004), MD-0002; watch items **W001–W004** da feature 006
- **Revisa parcialmente:** ADR 0009 (canonicidade agora per-projeto, não substituto global de `~/.claude`)
- **Completa:** ADR 0012 (adota a seção `[session]` ali adiada e fecha T2)

## Contexto e Problema

O MD-0004 registrara a intenção de tornar o `harness-core` "substituto da config global" (`~/.claude`), consolidando-o como referência canônica única (ADR 0009). Essa premissa tinha duas falhas. Primeiro, `~/.claude` é diretório do **fornecedor** (Claude Code): acoplar a memória durável a um layout que muda a cada atualização repete o erro do espelho `claude-config/` já purgado e reacopla o core a um único harness, desfazendo a neutralidade conquistada com `.harness/`. Segundo, uma mudança global tem raio de explosão sobre todos os projetos e não é versionada com o repositório — o oposto de reprodutível e reversível.

Restavam ainda dois resíduos das features anteriores: o caminho do estado de sessão seguia chumbado em `main.py` e divergente no MCP (T2, pendência `[session]` deixada explícita no ADR 0012), e a configuração tinha **duas vias** — `load_harness_config` (dict legado, via `import toml`) convivendo com `load_config` tipada (dívida T5).

## Decisão

Tratar o `harness-core` explicitamente como **módulo per-projeto autocontido, com footprint global zero**: instalá-lo ou executá-lo escreve **apenas** dentro do repositório, **nunca** em `~/.claude` ou `~/.agent-memory`. Dois níveis de memória ficam nomeados e sem competição — global (`~/.agent-memory`, repositório próprio) e per-projeto (`<repo>/.harness/`). Concretamente:

1. **Seção `[session]` por configuração:** `core/domain/config.py` ganha `class SessionSection(BaseModel): state_file: str = ".harness/estado-da-sessao.md"`, e `HarnessConfig` passa a ter o campo `session` (além de `harness`, `formatting`, `sync`, `decisions`). O `harness.toml` ganha `[session]` com `state_file = ".harness/estado-da-sessao.md"`. A CLI (`main.py:169`) e o MCP (`server.py:94`) leem `session_file = config.session.state_file`; nenhum literal de caminho de sessão sobrevive nos drivers (fecha T2 e a divergência CLI×MCP do ADR 0012).
2. **Via única tipada (T5 fechado):** `load_harness_config` (dict legado) e `import toml` são **removidos** de `main.py`. Toda a configuração passa por `load_config(fs)`; o subcomando `cmd` lê `config.harness.active_harness`, não `config["harness"]["active_harness"]`. Não há mais duas vias de configuração.
3. **Contrato de footprint testado:** novos `tests/test_footprint.py` e `tests/helpers.py` (`RecordingFileSystem`) fixam a invariante — o contrato **falha barulhento** se o harness escrever em `~/.claude`, `~/.agent-memory` ou fora do repositório. A zona protegida BR-MIGRAR-007 é preservada e agora **fixada por teste**.
4. **Reversão da premissa do MD-0004 (MD-0005):** o `harness-core` **não** substitui `~/.claude`; a canonicidade é PER-PROJETO. A aposentadoria do sync cross-harness (MD-0004) permanece válida — revista é só a premissa de canonicidade global.

## Alternativas Consideradas

- **Substituir `~/.claude` por symlink, variável de ambiente/XDG ou cópia:** descartada — estado global invisível, não versionado, e em tensão com a zona protegida BR-MIGRAR-007. Reintroduziria o acoplamento a um único harness e o raio de explosão global que motivaram o purge do `claude-config/`.
- **Absorver na 006 o RF-04 diferido da 005** (ensinar os scripts globais `~/.agent-memory/bin/*` a reconhecer `.harness/`): **diferido** para o repositório `agent-memory`, como mudança própria daquele repo — não deste. No projeto, o hook `Stop` → `./harness decisions` já cobre validação e índice.
- **Relaxar a zona protegida do `~/.claude`:** recusada — a blindagem é preservada e agora fixada por teste.
- **Manter a pendência `[session]` aberta (caminho chumbado):** preterida — perpetuaria a divergência CLI×MCP (T2). A seção `[session]` adiada no ADR 0012 foi adotada aqui.

## Consequências

- **Positivas:**
  - Módulo instalável com confiança em qualquer projeto e a um `git checkout` de distância de sumir — reprodutível e reversível.
  - Caminho de sessão desacoplado do layout físico (configurável); CLI e MCP convergem sobre o mesmo `config.session.state_file` (T2 fechado).
  - Via única de configuração tipada — fim das duas vias (T5 fechado), menos superfície de erro e de manutenção.
  - Footprint global zero fixado por teste, com falha barulhenta — a zona protegida BR-MIGRAR-007 deixa de depender de disciplina manual.
  - Neutralidade a harness preservada: a memória durável não reacopla ao diretório do fornecedor.
- **Negativas:**
  - 🟡 **Cobertura parcial do contrato:** `test_footprint.py` cobre só os serviços efetivamente exercitados — é teste, não guard de runtime; caminhos não exercidos não são capturados.
  - O RF-04 (scripts globais reconhecerem `.harness/`) fica como mudança futura no repositório `agent-memory`, fora do escopo deste repo.
