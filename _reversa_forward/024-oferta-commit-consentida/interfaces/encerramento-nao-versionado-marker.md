# Contrato (novo, 024): marker `[HARNESS:ENCERRAMENTO_NAO_VERSIONADO …]`

> Identificador: `024-oferta-commit-consentida`
> Tipo: protocolo de borda (core → agente), **pós**-fechamento
> Família: `COMMIT_PENDENTE` / `NARRATIVA_PENDENTE` / `DECISAO_PENDENTE`
> **Regeneração** — segunda versão; renomeado (era `REGISTRO_NAO_VERSIONADO`) e
> promovido de exceção a caminho default sob a RN-08

## 1. Propósito

Os três markers existentes são **pré**-fechamento e abortivos: anunciam algo a
resolver antes de encerrar. Este é o primeiro **pós**-fechamento e informativo: a
sessão foi encerrada, o estado foi gravado no arquivo, e o commit de encerramento
**não** foi criado.

Sob a RN-08, esse é o desfecho **default** do fluxo sem terminal — não uma
exceção rara. O agente que não pedir autorização ao usuário verá este marker toda
vez, e é ele que torna o esquecimento visível em vez de silencioso.

## 2. Quando é emitido

Sempre que o fechamento ocorre com `versionar_estado=False`:

- sem terminal, na ausência de `--com-commit-encerramento` (caso default);
- sem terminal, com `--sem-commit-encerramento` (recusa explícita);
- no terminal, quando o usuário responde `n` à pergunta, ou passa a flag de recusa.

Nunca é emitido quando o commit é criado.

## 3. Formato

```
[HARNESS:ENCERRAMENTO_NAO_VERSIONADO arquivo="<state_file>" ancora="<sha1 de 40>" motivo="<sem-autorizacao|recusa-explicita>" acao="o encerramento não foi versionado; para registrar depois: git add -- <state_file> && git commit; para autorizar na próxima vez, rode com --com-commit-encerramento"]
```

| Campo | Conteúdo | Obrigatório |
|-------|----------|-------------|
| `arquivo` | Caminho relativo do estado de sessão (ex.: `.harness/estado-da-sessao.md`) | sim |
| `ancora` | SHA-1 de 40 caracteres do último commit de trabalho, tal como gravado no estado | sim |
| `motivo` | `sem-autorizacao` (ninguém respondeu) ou `recusa-explicita` (flag ou `n`) | sim |
| `acao` | Instrução curta e estável para versionar depois e para autorizar na próxima | sim |

O campo `motivo` existe para o agente distinguir dois casos que exigem reações
diferentes: **esquecimento seu** (deve perguntar ao usuário agora) e **decisão do
usuário** (deve apenas confirmar o que ficou pendente).

## 4. Regras de processamento (lado do agente)

1. **Avisar o usuário** de que a sessão encerrou sem entrar no histórico e que o
   `arquivo` está como mudança pendente.
2. Se `motivo=sem-autorizacao`, reconhecer que a pergunta não foi feita: perguntar
   agora se ele quer versionar o encerramento.
3. **Não commitar por conta própria.** Autorizado, vale `git add -- <arquivo> &&
   git commit`, por caminho.
4. **Não reexecutar o encerramento**: a sessão já está fechada; reexecutar produz
   o no-op ruidoso de sessão ausente. Para versionar, commite o arquivo direto.

## 5. Invariantes

- Emitido **depois** da mensagem de sucesso do fechamento, nunca no lugar dela.
- A âncora reportada é a mesma gravada no estado: o último commit de **trabalho**.
- Convive com o aviso legível equivalente quando há terminal.
- Não bloqueia as ofertas de fim de sessão (push/upgrade), que seguem depois.

## 6. Borda a observar

Com o encerramento não versionado, a oferta de `push` (feature 014) pode continuar
cabível — há commits de trabalho à frente do remoto. Publicar trabalho cujo
registro de sessão ficou local é aceitável e **não** suprime a oferta; mas o aviso
deste marker precede a pergunta do push, para o usuário decidir informado.
