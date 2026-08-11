# Cápsula de reprodução — BUG-20260811-OYKV

## Ambiente

- **Artefato:** memória por-projeto do Claude Code em
  `~/.claude/projects/-Users-iagoleal-dev-comentarios-concursos/memory/ritual-de-encerramento-de-sessao.md`
  (externo ao repositório; nenhum código do harness envolvido).
- **Data da observação:** 2026-08-11. **Classificação:** deterministic (a memória é
  injetada em toda sessão do projeto). **Taxa:** 1/1.

## Reprodução

1. Abrir qualquer sessão do Claude Code em `/Users/iagoleal/dev/comentarios-concursos`.
2. A memória citada entra no contexto da sessão com dois fatos vencidos: o ritual de
   atualização do vault Obsidian no encerramento (abolido pela MD-0021) e a afirmação
   de que o harness fora desinstalado (o commit `3ff3f3f9` reinstalou o sistema de
   sessão via fonte única).
3. Ao pedir o encerramento, o agente guiado por ela reintroduz o passo do vault ou
   parte de premissa falsa sobre a ausência do harness.

Snapshot integral do artefato defeituoso como estava em 2026-08-11:
`ritual-de-encerramento-de-sessao-snapshot.md` (é a prova "antes"; o "depois" está em
`../fix/memoria-reescrita-depois.md`).

## Verificação pós-reparo

A memória reescrita declara: harness reinstalado (fonte única, commit `3ff3f3f9`),
encerramento via `/encerrar-sessao`, vault fora do fluxo (MD-0021); preservados os
fatos ainda válidos (remoto do vault é `origin`; trabalho direto na `main`). Não há
teste automatizado possível: o artefato vive fora do repositório e não é executável.
A verificação é a leitura comparada snapshot × versão atual.
