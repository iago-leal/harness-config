# Investigation: caminho de materialização do workflow Antigravity

> Feature `017-caminho-workflow-antigravity` · 2026-06-27

## 1. Pergunta de fundo

Por que o slash command `/encerrar-sessao`, materializado pelo Harness como workflow do Antigravity, não é reconhecido nem pela IDE nem pelo CLI?

## 2. Achados

- **Documentação oficial e guias derivados:** workflows do Antigravity residem em `.agent/workflows/` (singular); "files anywhere else are ignored". Frontmatter exige apenas `description` (≤250 caracteres); corpo ≤12.000 caracteres. O comando deriva do nome do arquivo (`encerrar-sessao.md` → `/encerrar-sessao`).
- **Glob literal do app instalado** (`/Applications/Antigravity IDE.app`): o seletor do _Workflow Editor_ aceita três padrões — `**/.agent/workflows/**/*.md`, `**/_agent/workflows/**/*.md`, `**/.agents/workflows/**/*.md`. Esse seletor governa qual editor abre o `.md`, não necessariamente o registro do slash command.
- **Evidência empírica no disco do mantenedor:** dos workflows que funcionam (`run-ipm-crew`, `PTEM`, `mcp_notebooklm`, `rede_social_rqe`, …), **100% estão em `.agent/` (singular)**; os únicos em `.agents/` (plural) foram gerados por Harness/Reversa — e é o `/encerrar-sessao` (plural) que falha.
- **Assimetria que arma a armadilha:** _skills_ do Antigravity vivem em `.agents/skills/` (plural) e _rules_ migraram para `.agents/rules/` (plural, com retrocompatibilidade para `.agent/rules/`); já _workflows_ permanecem em `.agent/workflows/` (singular). Quem materializou assumiu `.agents/` para tudo.

## 3. Hipóteses e veredito

Detalhe na §2.1 do `requirements.md`. Resumo: H1 (caminho plural) é a **causa-raiz confirmada**; H2 (loader varre só o singular) é provável; H3 (frontmatter com `name`) é improvável mas mitigável; H4 (nome do comando) e H5 (limite de 12k) descartadas.

## 4. Alternativas de solução avaliadas

| Alternativa                                       | Veredito      | Razão                                                                             |
| ------------------------------------------------- | ------------- | --------------------------------------------------------------------------------- |
| Gravar em `.agent/workflows/` (singular)          | **Escolhida** | Denominador comum reconhecido por todas as versões observadas (IDE e CLI).        |
| Manter `.agents/` (plural)                        | Rejeitada     | É a causa do defeito.                                                             |
| Gravar nos dois caminhos (singular e plural)      | Rejeitada     | Duplica o artefato e gera dois comandos potenciais; suja o projeto do consumidor. |
| Limpeza do órfão por hardcode na rotina           | Rejeitada     | Acopla `materialize_session_commands` ao detalhe do Antigravity.                  |
| Limpeza do órfão declarada pelo perfil            | **Escolhida** | Coesão: o perfil é dono dos seus caminhos; rotina agnóstica e extensível.         |
| Remover o diretório `.agents/workflows/` se vazio | Rejeitada     | Risco a terceiros; diretório vazio é inócuo.                                      |

## 5. Padrões aplicáveis

- **Strategy por harness** (`HarnessProfile`): cada perfil encapsula seu mecanismo e seus caminhos. O novo `stale_session_command_paths()` estende o mesmo padrão.
- **Materializador único** compartilhado por `init` e `upgrade` (`apply_local_materializers`, feature 012), executado com código fresco no upgrade (evita o bug stale).

## 6. Fontes externas

- Google Antigravity — Rules & Workflows: https://antigravity.google/docs/rules-workflows
- Mete Atamel — Customize Antigravity rules & workflows: https://atamel.dev/posts/2025/11-25_customize_antigravity_rules_workflows/
- agentpedia — Antigravity Workflows: https://agentpedia.codes/blog/workflows
- KD Agentic — Antigravity 2.0 Beginner's Guide: https://kd-agentic.medium.com/antigravity-2-0-beginners-guide-10-tips-to-master-google-s-multi-agent-platform-cf00fdf8316a
- Evidência local: glob do app `/Applications/Antigravity IDE.app`; inventário de workflows em `~/dev/**/.agent(s)/workflows/`.
