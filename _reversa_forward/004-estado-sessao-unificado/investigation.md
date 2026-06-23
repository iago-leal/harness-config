# Investigation — 004 estado de sessão unificado

> Data: 2026-06-23. Pesquisa de fundo e alternativas avaliadas para o roadmap.

## 1. Mecanismo de reinjeção por harness (verificado)

### Claude Code 🟢
Hook `SessionStart` (matcher `startup|resume|clear`) executa um comando; para injetar no contexto do modelo, o stdout (exit 0) traz:

```json
{ "hookSpecificOutput": { "hookEventName": "SessionStart", "additionalContext": "<texto>" } }
```

O texto entra como *system reminder*, sem virar mensagem de chat. Teto de **10.000 caracteres**. Exit 2 é bloqueante e o JSON é ignorado; outros exits são não-bloqueantes. Plain stdout também injeta em `SessionStart`, mas o JSON é o canal estruturado.
Fonte: doc oficial de hooks do Claude Code (`https://code.claude.com/docs/en/hooks.md`, 22/06/2026).

### Gemini CLI 🟢
Sistema de hooks com `SessionStart` (campo `source`: `startup`/`resume`/`clear`), configurado em `.gemini/settings.json`. **Mesmo contrato do Claude**: o comando emite no stdout `hookSpecificOutput.additionalContext`; em modo interativo o texto entra como primeiro turno do histórico. Sem limite de tamanho documentado.
Pré-requisito: **Gemini CLI ≥ 0.25** — hooks chegaram na 0.24, com regressão `#16697` (`SessionStart`/`SessionEnd` não disparavam) já corrigida; estável atual v0.45.
Fontes: `https://geminicli.com/docs/hooks/reference/`, `https://geminicli.com/docs/hooks/writing-hooks/`, issue `https://github.com/google-gemini/gemini-cli/issues/16697`.

### Antigravity (`agy`) 🟡
CLI é o binário `agy` (Go), config por projeto em `.agents/`, regras em `AGENTS.md`/`GEMINI.md`/`.agents/rules/*.md` (markdown estático relido a cada sessão). **Não há hook que injete stdout no contexto** — os hooks (`PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`) retornam decisão de controle (`allow`/`deny`/`ask`) sobre tool calls, não *prompt augmentation*. Contorno idiomático: o `cmd encerrar-sessao` escreve o estado num arquivo que o `agy` já relê (`.agents/rules/estado-sessao.md`), e a leitura é passiva no próximo boot.
Confiança média quanto aos nomes exatos dos hooks (doc oficial é SPA e não renderizou; lista veio do SDK GitHub e de deep-dives). Exige teste de fumaça.
Fontes: Google Cloud Blog "Choosing your surface" (10/06/2026), `https://github.com/google-antigravity/antigravity-sdk-python`, fórum AI Developers (thread "Hook support for context-mode" — feature ainda não suportada).

## 2. Alternativas avaliadas

| Alternativa | Veredito | Razão |
|-------------|----------|-------|
| Mecanismo único para os três harnesses | descartada | Antigravity não injeta stdout; forçaria um caminho que não existe |
| Wrapper shell + `jq` para envelopar o Gemini | descartada | Desnecessário: o `cmd resume` emite o JSON direto, que serve Claude e Gemini |
| Antigravity via MCP resource | descartada | Mais "vivo", mas exige o agente decidir chamar e adiciona servidor a manter |
| JSON puro como formato do arquivo de estado | descartada | Ilegível como narrativa; o front-matter YAML + corpo Markdown é legível e testável |
| Local na raiz `estado-da-sessao.md` | descartada | Polui a raiz; `.harness/` agrupa e fica neutro (MD-0003 / decisão do mantenedor) |
| Manter dois arquivos por concern (JSON + MD) | descartada | Reinstitui o drift que o MD-0001 criou |

## 3. Resolução proposta para a `[DÚVIDA]` do Antigravity 🟡

Sem hook de injeção, a reinjeção de contexto no Antigravity é **passiva**: o `cmd encerrar-sessao` materializa `.agents/rules/estado-sessao.md` (projeção do canônico) e o `agy` o relê no boot seguinte. Para preservar o check de divergência de âncora (RN-07 / `state-machines.md#1`), propõe-se um hook de pré-invocação do `agy` (`PreInvocation` ou equivalente) rodando `cmd resume` em modo sem-injeção, que valida a âncora e atualiza o status. Se o hook não existir ou divergir, o ramo degrada para reinjeção passiva pura (sem validação ativa), ainda funcional. A confirmação é teste de fumaça no `onboarding.md`.

## 4. Padrões aplicáveis

- **Strategy** (GoF) para a entrega por-harness, reusando o padrão já estabelecido em `core/install/harness_profiles.py` (feature 003).
- **Value Object** (`SessionNarrative`) imutável dentro do agregado `SessionState`.
- **Round-trip property testing**: `parse(render(x)) == x` como invariante de serialização (pytest, já no projeto).
- Reuso de `pyyaml` (front-matter, já usado em `DecisionService`) e `pydantic` (validação, já usado em `models.py`) — zero dependência nova.
