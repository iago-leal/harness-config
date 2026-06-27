# Investigation: Correção do no-op silencioso no `encerrar-sessao`

> Identificador: `015-corrige-encerrar-sessao-noop`
> Data: `2026-06-27`

## 1. Pergunta de fundo

Por que o `encerrar-sessao` "às vezes nem commita", devolvendo um sucesso aparente? E qual o menor delta que restaura o princípio de erros barulhentos sem regredir o boot do agente?

## 2. Achados por leitura de código

Dois caminhos distintos convergem para o mesmo sintoma — `exit 0` sem fechamento:

1. **Hash curto (estado malformado).** `commands/service.py::load_session` → `session/serializer.py::parse` levanta `MalformedSessionStateError` para commit não-SHA1 (entre outras corrupções; `serializer.py:40-107`). A borda `cmd` em `main.py` captura essa exceção num único `except` que faz `print(... stderr)` + `sys.exit(0)`. O comentário no código justifica o `exit 0` como proteção do `SessionStart`.
2. **Sessão válida porém inativa.** `execute_command`, ramo `encerrar-sessao`, testa `if not session or not session.is_active` e **retorna a string** `"Erro: Nenhuma sessão ativa encontrada para encerrar."` (`service.py:40-41`). A borda imprime no ramo `else` e cai no `sys.exit(0)` final incondicional. As ofertas de fim de sessão (014) só rodam se o retorno começa com `"Sessão encerrada com sucesso"`, então nada acontece.

Ponto-chave: o `RN-N4` (`domain.md#2.3`) classifica apenas **ausente** vs **malformado**. A sessão _válida porém inativa_ é uma terceira categoria que a regra não cobre — daí o segundo no-op nunca ter sido tratado como erro.

## 3. Sinal de fronteira reaproveitável

A borda já distingue boot de explícito: `if cmd_name_norm == "resume"` escolhe o sink de reinjeção (`main.py`). O mesmo nome de comando basta para decidir o exit code, sem introduzir flag de ambiente nem heurística de TTY. Isso sustenta D-02.

## 4. Alternativas avaliadas

| Alternativa                                                                       | Avaliação                                                                                                    | Veredito                    |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | --------------------------- |
| Inspecionar o prefixo `"Erro:"` do retorno na borda                               | Acopla a borda ao texto da mensagem; quebra silenciosamente se a string mudar                                | Descartada                  |
| Service decide e retorna o exit code                                              | Viola RN-N5 (o core não conhece a borda nem o ciclo de boot)                                                 | Descartada                  |
| Auto-reparo do hash curto (expandir prefixo → SHA-1 de 40)                        | Boa UX, mas adiciona caminho com casos de borda (prefixo ambíguo, não resolve); contraria a queixa de leveza | Adiada (decisão de clarify) |
| Novo comando `iniciar-sessao` para reativar fora do boot                          | Ciclo de vida simétrico, porém amplia superfície de comandos e materialização                                | Adiada (decisão de clarify) |
| Exceção nomeada `NoActiveSessionError` + ramificação na borda por nome do comando | Barulhento por tipo, coeso com `SessionCommitError`, core agnóstico, delta mínimo                            | **Escolhida** (D-01/D-02)   |

## 5. Padrão aplicável

Erro nomeado por categoria + decisão de apresentação na borda é o padrão já estabelecido no core: `MalformedSessionStateError` (estado), `SessionCommitError` (commit). `NoActiveSessionError` segue o mesmo molde — consistência interna, sem novo paradigma.

## 6. Fontes

- `_reversa_sdd/domain.md#2.3` (RN-N3, RN-N4), `#2.14` (RN-N31/N32)
- `_reversa_sdd/architecture.md#3` (serviço de comandos), `#4` (borda de integração)
- Código (apoio): `src/core/commands/service.py`, `src/core/commands/errors.py`, `src/core/session/serializer.py`, `src/main.py` (despacho `cmd`)
