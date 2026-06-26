# Interface: saída das ofertas de fim de sessão

> Identificador: `014-oferta-upgrade-ao-encerrar`
> Tipo: contrato de borda — produzido por `main.py` (ramo `cmd encerrar-sessao`)
> Consumidores: humano no terminal (modo TTY) e agente de IA (modo slash command, sem TTY)

A borda decide o modo por `sys.stdin.isatty()` (molde `offer_git_init`). A ordem é sempre
**push → upgrade** (RN-10). A mensagem de encerramento (013, os dois hashes) é impressa
**antes** das ofertas e nunca é suprimida (RN-02).

## Modo TTY (terminal interativo)

Para cada oferta cabível, uma pergunta `[s/N]` em sequência:

```
<mensagem de encerramento da sessão (013)>

Há 3 commit(s) à frente de origin/feature-x. Publicar agora (git push)? [s/N]
```

Na branch principal, o texto recebe o aviso reforçado (RN-05):

```
⚠️  'main' é a branch principal. Publicar diretamente em origin/main (git push)? [s/N]
```

Em seguida (se aplicável):

```
🔼 Atualização do Harness Core disponível: 1.2.49 → 1.3.0. Atualizar agora? [s/N]
```

- Resposta afirmativa (`s`/`sim`/`y`/`yes`) executa a ação; qualquer outra pula.
- Aceitar o upgrade: sincroniza o upstream por fast-forward (D-05) e então roda `upgrade_project`;
  falha de sincronização aborta o upgrade barulhento, sem travar o comando.

## Modo sem TTY (slash command / agente)

Sem leitura de entrada. A borda imprime, no `stdout`, **uma linha-marcador estável por oferta**
cabível, que o agente reconhece e medeia no chat. Formato (tokens `chave=valor`):

```
[HARNESS:PUSH_DISPONIVEL branch=feature-x remote=origin ahead=3 principal=false acao="./harness ... (git push)"]
[HARNESS:UPGRADE_DISPONIVEL atual=1.2.49 alvo=1.3.0 acao="./harness upgrade"]
```

Regras do marcador:

- Prefixo fixo `[HARNESS:` + tipo (`PUSH_DISPONIVEL` | `UPGRADE_DISPONIVEL`) + tokens + `]`.
- Uma linha por oferta; só aparece a oferta que se aplica.
- `principal=true` sinaliza ao agente que deve reforçar o aviso antes de confirmar com o usuário.
- Texto livre adicional pode acompanhar para leitura humana, mas o marcador é a âncora de parse.
- O agente, ao ver o marcador, pergunta ao usuário no chat e, com o "sim", executa a `acao`
  correspondente (`git push` no diretório do projeto; `./harness upgrade`).

## Erros e degradação (ambos os modos)

- Falha de rede/auth na detecção de upgrade → nenhuma linha `UPGRADE_DISPONIVEL`; aviso em `stderr`.
- Sem upstream tracking ou branch em dia → nenhuma linha `PUSH_DISPONIVEL`.
- Falha de `push`/`upgrade`/sincronização → aviso em `stderr`; encerramento permanece válido (exit 0
  do encerramento não é revertido pela oferta). RN-02/RN-09.

## Idempotência e timeouts

- Idempotente quanto ao encerramento: reexecutar o comando após o estado já encerrado cai no
  ramo "nenhuma sessão ativa" e não dispara ofertas (D-10).
- `fetch`/`push` herdam timeouts do git/host; uma demora não trava o encerramento porque a etapa
  roda após o fechamento e sob `try/except` (não há rollback do commit de estado).
