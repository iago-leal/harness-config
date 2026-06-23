---
schemaVersion: 1
generatedAt: "2026-06-23T14:07:00Z"
reversa:
  version: "1.2.43"
kind: discard_log
producedBy: curator
hash: "sha256:e868e6cb4e26feb70d885f27cf611ed2ae28db9c9c8549d0be67dcbbc37015e7"
---

# Discard Log

> Registro completo do que foi descartado da migração e por quê. Cada item tem rastreabilidade para a origem no legado.

## Itens descartados

### BR-DESCARTAR-001
- **Origem**: `_reversa_sdd/format-on-edit/contracts.md`
- **Descrição**: Emissão de JSON específico em stdout para o Claude Code (como `{"systemMessage": "🎨 prettier padronizou..."}` pós-formatação e payloads `{hookSpecificOutput: ...}` no SessionStart).
- **Justificativa**: Na nova stack agnóstica baseada na Opção A (Portas e Adaptadores em Python), o domínio técnico encapsula regras genéricas de retorno de mensagens. Os formatos físicos exigidos por ganchos específicos são isolados na camada de infraestrutura (Adaptadores de Saída de IDE), limpando o domínio de acoplamento direto de layouts específicos do Claude.
- **Vinculado a paradigma**: Sim
  - Como o paradigma alvo absorve o caso: O core Python expõe classes abstratas de retorno. O adaptador `ClaudeAdapter` herda essa classe e implementa a serialização JSON exata exigida pelo Claude Code.
- **Reposição no sistema novo**: Substituído por injeção do adaptador `ClaudeAdapter` na CLI.
- **Risco de descartar**: Baixo.

### BR-DESCARTAR-002
- **Origem**: `_reversa_sdd/format-on-edit/requirements.md` § Requisitos Funcionais
- **Descrição**: Mapeamento físico fixo e rígido de diretórios do Claude Code (`~/.claude/` e `settings.json`) como locais únicos de instalação e arquivos de configuração.
- **Justificativa**: Viola a premissa de agnosticismo cross-harness. O sistema novo deve parametrizar seus caminhos de configuração e de ganchos em um arquivo local genérico `harness.toml`.
- **Vinculado a paradigma**: Sim
  - Como o paradigma alvo absorve o caso: O script compilador Python lê o `harness.toml` do projeto de trabalho e injeta/compila os caminhos físicos adequados para cada Harness ativo.
- **Reposição no sistema novo**: Substituído por configuração centralizada no `harness.toml`.
- **Risco de descartar**: Baixo.

---

## Itens descartados por mudança de paradigma (subseção dedicada)

| ID | Origem | Paradigma legado | Substituto no paradigma alvo |
| :--- | :--- | :--- | :--- |
| **BR-DESCARTAR-001** | `_reversa_sdd/format-on-edit/contracts.md` | Saída em stdout acoplada à IDE específica | Adaptador de Saída (`ClaudeAdapter`) |
| **BR-DESCARTAR-002** | `_reversa_sdd/format-on-edit/requirements.md` | Instalação fixa em caminhos do Claude | Compilador Python + Configuração em TOML |
