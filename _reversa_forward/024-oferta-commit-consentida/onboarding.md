# Onboarding: como testar a oferta de commit consentida

> Identificador: `024-oferta-commit-consentida`
> Data: `2026-07-23`
> Público: você, daqui a alguns meses, querendo confirmar que a feature funciona
> **Regeneração** — segunda versão, com os cenários do default invertido (RN-08)

## 0. Por que o smoke é manual e com git real

Os testes automatizados usam um `FakeGit` que entrega `list_dirty_paths` já
expandido e **esconde** o colapso do `git status --porcelain` em subdiretórios
não rastreados. A feature 019 pagou esse preço. A suíte é obrigatória, mas não
suficiente: os cenários abaixo rodam com git de verdade, num repositório
descartável, nunca no repo do harness.

## 1. Preparar um repositório descartável

```bash
cd "$(mktemp -d)"
git init -b main
git config user.email teste@local && git config user.name Teste
echo "# projeto de teste" > README.md
git add README.md && git commit -m "commit inicial"

~/dev/harness/harness init .
```

Confirme antes de seguir:

```bash
ls .harness/estado-da-sessao.md && ./harness --version
```

## 2. Abrir uma sessão e produzir trabalho

```bash
./harness cmd resume feature-de-teste
echo "trabalho real" > arquivo-a.txt
mkdir -p sub && echo "trabalho em subpasta" > sub/arquivo-b.txt
```

Escreva algo nas quatro seções `##` do `.harness/estado-da-sessao.md` — sem isso
o portão de narrativa aborta antes de você chegar ao que interessa.

## 3. Cenário A — pergunta em vez de ordem (terminal)

```bash
./harness cmd encerrar-sessao
```

**Esperado:**

- A **contagem** encabeça a saída: `há 2 mudanças não commitadas`.
- Os caminhos vêm logo abaixo (no terminal a lista aparece; para o agente, não).
- Pergunta sobre encerrar mesmo assim (`[s/N]`), **não** uma ordem de commitar.
- Respondendo `n`: nada commitado, sessão **não** fecha.

**Sinal de regressão:** o texto imperativo antigo "Commit esse trabalho (git add
…) e rode encerrar-sessao novamente".

## 4. Cenário B — encerrar mesmo com trabalho sujo

```bash
./harness cmd encerrar-sessao   # responda 's' à pergunta de segunda ordem
```

**Esperado:**

- A sessão encerra; a saída diz quais mudanças ficaram fora do histórico.
- `git status` ainda mostra `arquivo-a.txt` e `sub/arquivo-b.txt`.
- A narrativa ganhou a linha declarativa de encerramento com pendências.

Confira que a subpasta não rastreada aparece **por arquivo**, não colapsada:

```bash
git status --porcelain --untracked-files=all
```

## 5. Cenário C — commit de encerramento consentido (terminal)

```bash
git add -- arquivo-a.txt sub/arquivo-b.txt && git commit -m "feat: trabalho de teste"
./harness cmd resume feature-de-teste
# edite a narrativa
./harness cmd encerrar-sessao   # responda 's' (ou Enter: default afirmativo)
```

**Esperado:**

- Pergunta sobre gravar o commit de encerramento, com default `[S/n]`.
- Commit contendo **exclusivamente** `.harness/estado-da-sessao.md`:

```bash
git show --stat --name-only HEAD
```

- A âncora reportada aponta para o commit de **trabalho**, não para o de encerramento.

## 6. Cenário D — commit de encerramento recusado (terminal)

Repita o ciclo e responda `n`:

**Esperado:**

- A sessão encerra (front-matter fechado no arquivo).
- **Nenhum** commit novo: `git log --oneline -1` segue no commit de trabalho.
- `git status` mostra `.harness/estado-da-sessao.md` modificado.
- Marker/aviso com `motivo=recusa-explicita`.
- Narrativa com a linha declarativa de encerramento não versionado.

## 7. Cenário E — o default invertido, sem terminal (o mais importante)

Este é o cenário que a RN-08 criou e o que a auditoria salvou. Simule a ausência
de terminal redirecionando a entrada:

```bash
./harness cmd resume feature-de-teste
# edite a narrativa; deixe a árvore limpa (commite o que houver)
./harness cmd encerrar-sessao < /dev/null
```

**Esperado:**

- **Nenhum commit criado** — este é o ponto: sem autorização, não versiona.
- `[HARNESS:ENCERRAMENTO_NAO_VERSIONADO arquivo="…" ancora="…" motivo=sem-autorizacao acao="…"]`.
- Nenhuma tentativa de ler entrada (nada de `EOFError`).

Agora com autorização declarada:

```bash
./harness cmd resume feature-de-teste
# edite a narrativa
./harness cmd encerrar-sessao --com-commit-encerramento < /dev/null
```

**Esperado:**

- Commit de encerramento criado, com o `state_file` apenas.
- **Nenhum** marker de aviso.

## 8. Cenário F — flags exclusivas e pendência sem terminal

```bash
./harness cmd encerrar-sessao --com-commit-encerramento --sem-commit-encerramento < /dev/null
```

**Esperado:** erro de uso barulhento (código ≠ 0), sem encerrar nada.

E com trabalho sujo, sem terminal:

```bash
echo "novo trabalho" > arquivo-c.txt
./harness cmd encerrar-sessao < /dev/null                    # marker COMMIT_PENDENTE, não fecha
./harness cmd encerrar-sessao --com-pendencias < /dev/null   # fecha, com aviso
```

## 9. Cenário G — duas sessões encadeadas sem versionar

Depois de um encerramento não versionado:

```bash
./harness cmd resume feature-de-teste
```

**Esperado:**

- **Sem** o `⚠️ ALERTA` de divergência de âncora (HEAD e âncora coincidem).
- A narrativa reinjetada mostra a linha declarativa do encerramento não versionado.
- O `estado-da-sessao.md` sujo **não** dispara o pré-check de pendência ao
  encerrar de novo — é excluído por caminho exato.

Este é o cenário que a feature mais arrisca quebrar. Se algo falhar, é aqui.

## 10. Paridade das bordas

Tudo acima vale igualmente pelo script fino da skill:

```bash
python3 .claude/skills/encerrar-sessao/scripts/encerrar_sessao.py --help
```

As quatro flags — `--sem-decisao`, `--com-pendencias`,
`--com-commit-encerramento`, `--sem-commit-encerramento` — precisam aparecer nas
**duas** bordas. Divergência aqui é regressão da RN-N33.

## 11. Limpeza

```bash
cd ~ && rm -rf "$OLDPWD"   # confira que $OLDPWD é mesmo o diretório temporário
```
