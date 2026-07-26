# Contrato (delta 024): flags de encerramento

> Identificador: `024-oferta-commit-consentida`
> Tipo: linha de comando (duas bordas)
> Base: flag `--sem-decisao` (feature 022), mesma família
> **Regeneração** — segunda versão, após a RN-08 inverter o default sem terminal

## 1. Superfície

As **duas** bordas expõem o mesmo conjunto (paridade exigida pela RN-N33):

| Borda | Invocação |
|-------|-----------|
| CLI | `./harness cmd encerrar-sessao [--sem-decisao] [--com-pendencias] [--com-commit-encerramento \| --sem-commit-encerramento]` |
| Script fino da skill | `python3 scripts/encerrar_sessao.py` com as mesmas flags |

Ambas repassam ao mesmo `SessionCloseFlow.run(...)`. Divergência de superfície
entre elas é regressão da fonte única.

## 2. Semântica

| Flag | Efeito | Portão afetado |
|------|--------|----------------|
| `--sem-decisao` | Declara que não houve decisão não óbvia; grava a declaração na narrativa e libera o portão | 3º (registro de decisões, 022) |
| `--com-pendencias` | Autoriza encerrar **com** trabalho não commitado; grava a declaração na narrativa e libera o portão | 1º (pré-check de pendência, 016/019) |
| `--com-commit-encerramento` | **Autoriza** gravar o commit de encerramento | fechamento (013/RN-N31) |
| `--sem-commit-encerramento` | **Recusa** explicitamente o commit de encerramento | fechamento (013/RN-N31) |

As duas últimas são **mutuamente exclusivas** (D-08): passar ambas é erro de uso,
resolvido pelo grupo mutuamente exclusivo do `argparse`, com saída barulhenta e
código ≠ 0. Ambiguidade sobre escrita no histórico não se resolve por precedência
silenciosa.

Nenhuma flag implica outra: `--com-pendencias` **não** implica autorização do
commit de encerramento. É legítimo encerrar com trabalho sujo e ainda assim
versionar o estado.

## 3. Matriz de resolução (o coração do contrato)

O default do commit de encerramento **depende da borda** (D-07/RN-08):

| Modo | Flag | Resultado |
|------|------|-----------|
| Terminal interativo | nenhuma | **Pergunta** `[S/n]`, default afirmativo |
| Terminal interativo | `--com-commit-encerramento` | Versiona, sem perguntar |
| Terminal interativo | `--sem-commit-encerramento` | Não versiona, sem perguntar; emite o marker de aviso |
| Sem terminal | nenhuma | **Não versiona** e emite o marker de aviso |
| Sem terminal | `--com-commit-encerramento` | Versiona |
| Sem terminal | `--sem-commit-encerramento` | Não versiona; idêntico ao default, porém explícito no rastro |

Duas regras derivadas, que valem como invariante de teste:

1. **Flag explícita sempre vence a pergunta.** Quem digitou a flag já respondeu.
2. **Silêncio sem terminal nunca autoriza escrita.** A ausência de resposta é
   tratada como recusa, não como consentimento (RN-08).

## 4. Assinatura interna correspondente

```python
SessionCloseFlow.run(
    repo_path, config, *,
    out=print, err=None, asker=_ask_yes, is_interactive=None,
    sem_decisao: bool = False,
    com_pendencias: bool = False,              # novo
    versionar_encerramento: Optional[bool] = None,  # novo: None = não respondido
) -> int
```

`versionar_encerramento` é **tri-estado** por necessidade: `True` (autorizado),
`False` (recusado) e `None` (não respondido — resolver pelo default da borda). Um
booleano de dois estados não distingue "recusou" de "não disse", e é exatamente
essa distinção que a RN-08 exige.

Um nível abaixo, o serviço permanece binário, porque recebe a decisão já tomada:

```python
CommandService.execute_command(
    command, args, repo_path, session_filepath,
    versionar_estado: bool = True,   # novo
) -> str
```

O default `True` preserva todos os chamadores atuais, inclusive o adaptador MCP
(`src/adapters/mcp/server.py:98`), que não muda (D-04).

## 5. Códigos de saída

| Situação | Código |
|----------|--------|
| Fechamento concluído (versionado ou não) | 0 |
| Aborto por portão (pendência / narrativa / decisão) | 0 — aborto esperado, não erro |
| Flags mutuamente exclusivas juntas | 2 (erro de uso do `argparse`) |
| Estado malformado | 1 |
| Falha de `commit_paths` quando o commit **foi** autorizado | 1 |

Recusar o commit de encerramento **não** é falha: sai 0, com aviso.

## 6. Ajuda (`--help`)

Os textos devem dizer a consequência, não o efeito mecânico:

- `--com-pendencias`: "Encerra mesmo havendo trabalho não commitado (a declaração
  fica registrada na narrativa)."
- `--com-commit-encerramento`: "Autoriza versionar o estado de sessão ao
  encerrar. Sem terminal interativo, sem esta flag o estado não é versionado."
- `--sem-commit-encerramento`: "Encerra sem versionar o estado de sessão; ele
  fica como mudança pendente no working tree."
