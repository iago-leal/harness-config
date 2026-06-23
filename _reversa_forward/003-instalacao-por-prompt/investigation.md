# Investigation: Instalação do Harness por Prompt Estruturado

> Identificador: `003-instalacao-por-prompt`
> Data: `2026-06-23`

## 1. Pesquisa de fundo

A instalação atual (descrita no `onboarding.md` da feature 001) é uma sequência manual de quatro etapas no terminal: criar a venv, instalar dependências, garantir o wrapper executável, aplicar os ganchos no `settings.json`. Cada etapa é um ponto de fricção e de erro silencioso para um mantenedor que retoma o projeto após meses. A `architecture.md#5-dividas-tecnicas-identificadas` já apontava o setup de dependências como o ponto frágil (dependência implícita de interpretador global).

O núcleo já tem o **mecanismo certo** para resolver isso sem inventar nada: o `DocumentationService` (feature 002) gera o `harness-docs.html` por **introspecção do `argparse.ArgumentParser`** (RN-10, introspecção dinâmica). O mesmo padrão serve ao prompt de instalação — derivar o texto da realidade do código, não de uma cópia mantida à mão.

## 2. Alternativas avaliadas

| Alternativa | Prós | Contras | Veredito |
|-------------|------|---------|----------|
| Comando da CLI por introspecção (`install-prompt`) | Fonte única, sem drift, testável, coeso com a CLI | Exige um módulo novo | **Escolhida** (D-01, D-02) |
| Markdown estático na raiz (`INSTALACAO.md`) | Simples, zero código | Índice paralelo que dessincroniza (proibido pelo ALICERCE) | Descartada |
| Script shell instalador (`install.sh`) | Executa direto | Acoplado a caminhos, difícil de testar, foge do paradigma OOP do core | Descartada |
| Makefile / task runner | Convencional | Nova dependência de ferramenta; não é "colável no agente" | Descartada |

## 3. Padrões aplicáveis

- **Introspecção (já no projeto):** `DocumentationService.extract_commands` percorre `parser._actions` e os subparsers. O `InstallPromptService` reaproveita a mesma técnica para listar comandos e montar a etapa de verificação de saúde.
- **Strategy (Gang of Four):** um perfil por harness (`claude`, `gemini`, `antigravity`) encapsula o mecanismo de aplicação dos ganchos, evitando `if/elif` espalhado e permitindo extensão sem tocar o serviço (D-04, OOP).
- **Template Method / render por substituição:** o template do prompt (`core/install/template.md`) tem placeholders preenchidos pelo serviço, como o `template.html` do `DocumentationService`.
- **Detect-then-complete (idempotência):** cada passo do prompt instrui o agente a checar o que já existe antes de criar, satisfazendo RN-02.

## 4. Mecanismos de hook por harness (fontes)

- **claude** 🟢: `.claude/settings.json` com a chave `hooks` (`SessionStart`/`PostToolUse`/`Stop`), formato já validado pelo corte da MD-0001.
- **gemini** 🟡: a configuração de memória/hooks usa a ponte `context.*` no `settings.json` do Gemini (ALICERCE, `docs/SPEC-memoria-no-gemini.md`), não o mesmo esquema do Claude. O perfil precisa refletir isso.
- **antigravity** 🔴: mecanismo de ganchos ainda não documentado no `_reversa_sdd/`. Fica como lacuna a confirmar antes de marcar o perfil como pronto.

## 5. Fontes consultadas

- `_reversa_sdd/architecture.md` (estilo hexagonal, dívidas técnicas)
- `_reversa_sdd/code-analysis.md#26-modulo-documentation` (padrão de introspecção)
- `_reversa_sdd/domain.md` (RN-10 introspecção; `active_harness`)
- `_reversa_forward/001-run-harness-core-local/onboarding.md` (procedimento manual atual)
- `decisoes/MD-0001.md` (corte dos hooks; regressão do SessionStart)
- ALICERCE / `docs/SPEC-memoria-no-gemini.md` (ponte `context.*` do Gemini)
