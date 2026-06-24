# Onboarding: testar o comando de encerrar a sessão

> Identificador: `010-command-encerrar-sessao`
> Data: `2026-06-24`
> Público: humano testando a feature pela primeira vez. Tempo estimado: < 5 min.

## Pré-requisitos

- `python3` e `git` no PATH.
- Estar na raiz do repositório upstream do harness (`/Users/iagoleal/dev/harness`).

## Passo a passo

1. **Crie um projeto-alvo descartável e inicialize git:**

   ```bash
   mkdir -p /tmp/harness-smoke && cd /tmp/harness-smoke && git init -q
   ```

2. **Rode o `init` a partir do upstream** (qualquer `--harness`, pois a materialização é incondicional):

   ```bash
   /Users/iagoleal/dev/harness/harness cmd >/dev/null 2>&1 || true   # aquece o ambiente, opcional
   /Users/iagoleal/dev/harness/harness init /tmp/harness-smoke --harness claude
   ```

3. **Verifique que os dois arquivos de comando existem:**

   ```bash
   ls -1 /tmp/harness-smoke/.claude/commands/encerrar-sessao.md \
         /tmp/harness-smoke/.agents/workflows/encerrar-sessao.md
   ```

   Esperado: as duas linhas listadas, sem erro.

4. **Confirme o conteúdo aciona o `./harness cmd encerrar-sessao`:**

   ```bash
   grep -n "cmd encerrar-sessao" /tmp/harness-smoke/.claude/commands/encerrar-sessao.md
   grep -n "cmd encerrar-sessao" /tmp/harness-smoke/.agents/workflows/encerrar-sessao.md
   ```

   Esperado: o Claude referencia `./harness cmd encerrar-sessao` (relativo à raiz); o Antigravity referencia o caminho absoluto do projeto.

5. **Exercite o efeito real (sessão ativa → encerrada):**

   ```bash
   cd /tmp/harness-smoke
   ./harness cmd resume feature-teste     # abre uma sessão
   ./harness cmd encerrar-sessao          # o que o slash command dispara
   ```

   Esperado: a segunda chamada responde "Sessão encerra com sucesso na feature 'feature-teste' com commit âncora <hash>".

6. **Confirme o footprint zero** (nada escrito fora do projeto):

   ```bash
   ls ~/.claude/commands/encerrar-sessao.md 2>/dev/null && echo "FALHA: escreveu global" || echo "OK: nada no global"
   ```

   Esperado: `OK: nada no global`.

7. **Verifique a idempotência do `upgrade`:**

   ```bash
   cd /tmp/harness-smoke && ./harness upgrade
   ls -1 .claude/commands/encerrar-sessao.md .agents/workflows/encerrar-sessao.md
   ```

   Esperado: os arquivos continuam presentes e inalterados em estrutura.

8. **Limpe:**
   ```bash
   rm -rf /tmp/harness-smoke
   ```

## Verificação automatizada (quando o código existir)

```bash
cd /Users/iagoleal/dev/harness/harness-core && .venv/bin/python -m pytest tests/test_session_commands_materializer.py -q
```

Esperado: verde, incluindo o teste de footprint (`RecordingFileSystem`).
