# Data Delta: Correção do no-op silencioso no `encerrar-sessao`

> Identificador: `015-corrige-encerrar-sessao-noop`
> Data: `2026-06-27`

## Resumo

**Sem mudança no modelo de dados persistido.** O `SessionState` — campos, formato canônico em `.harness/estado-da-sessao.md`, round-trip do `serializer` (`parse`/`render`) — permanece idêntico. A feature é puramente comportamental: corrige códigos de saída e mensagens na borda.

## Campos novos

Nenhum.

## Campos removidos

Nenhum.

## Migração de dados

n/a. Nenhum estado existente precisa ser reescrito.

> Nota: o estado legado de **hash curto** continua sendo lido como malformado. A feature **não** o auto-repara (decisão de clarify); a correção manual única — regravar a âncora com o SHA-1 de 40 caracteres — é guiada pela mensagem de erro barulhenta. Isso é correção pontual de dado pelo usuário, não migração automatizada.

## Novidade de runtime (não persistida)

- `NoActiveSessionError` (`src/core/commands/errors.py`): exceção nomeada levantada quando se tenta encerrar uma sessão inexistente ou inativa. Vive apenas em tempo de execução; não aparece em nenhum arquivo de estado.
