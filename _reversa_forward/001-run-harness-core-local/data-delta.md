# Data Delta: Execução Local do Harness Core

> Identificador: `001-run-harness-core-local`
> Data: `2026-06-23`

## 1. Mapeamento de Entidades Físicas

Não existem bancos de dados relacionais ou esquemas de dados persistidos afetados por esta feature.
O estado do sistema continua sendo gerenciado por:
- `ESTADO-DA-SESSAO.md` (no formato Markdown, mapeando as transições de sessão).
- `.reversa/active-requirements.json` (usado pelo Reversa para controle de features).

## 2. Modificações Conceituais de Estado

Não há novos modelos de dados ou campos a serem adicionados às tabelas ou arquivos JSON estruturados.
A única alteração física é a criação de arquivos utilitários de ciclo de vida (`./harness` na raiz).

## 3. Scripts de Migração de Dados

Não aplicável (n/a).
