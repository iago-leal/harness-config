# Regression watch: 024-oferta-commit-consentida

> Identificador: `024-oferta-commit-consentida`
> Gerado por `/reversa-coding` em 2026-07-24.

## Watch items

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|
| W001 | `commands/service.py` (024/D-03, RF-08) | `execute_command` tem `versionar_estado: bool = True`; com `False`, fecha sem `commit_paths` e grava a linha declarativa na narrativa | presença | Parâmetro ausente; `commit_paths` chamado mesmo com `versionar_estado=False`; teste `test_execute_encerrar_sessao_sem_versionar_fecha_sem_commit` removido |
| W002 | `close_flow.py`, `SessionCloseFlow.run` (024/D-07, RN-08) | Sem terminal e sem flag, o commit de encerramento **não** ocorre (`versionar_encerramento=None` → recusa); no terminal, pergunta `[S/n]` com default afirmativo | redação | Default sem terminal voltando a versionar; `_resolve_versionar_encerramento` tratando `None` como autorização sem terminal |
| W003 | `close_flow.py`, `render_encerramento_nao_versionado_marker` (024/RF-09) | Fechamento sem versionar emite `[HARNESS:ENCERRAMENTO_NAO_VERSIONADO arquivo/ancora/motivo/acao]`, depois do sucesso e antes da oferta de push | presença · redação | Marker ausente num caminho que fecha sem versionar; ordem invertida vs. a oferta de push; `motivo` fora de `{sem-autorizacao, recusa-explicita}` |
| W004 | `close_flow.py`, `conduct_commit_pendente` (024/RF-01/RF-04/RN-06) | No terminal anuncia a contagem à frente ("há N mudança(s) não commitada(s)"), lista os caminhos e devolve a autorização do `asker`; sem terminal emite o marker e devolve `False` | redação | Volta ao texto imperativo antigo ("Commit esse trabalho…"); função não devolvendo `bool`; contagem fora da frente |
| W005 | `close_flow.py`, marker `COMMIT_PENDENTE` (024/RF-01/RF-10) | O campo `acao` descreve a **oferta** (perguntar antes; `--com-pendencias` como saída da recusa); `arquivos`/`total`/`truncado`/`mostrados` e o teto de 20 preservados byte a byte | redação | `acao` voltando a ordenar commit; qualquer mudança no formato dos demais campos |
| W006 | `main.py` (`cmd`) + script fino (024/D-08, RN-N33) | As três flags (`--com-pendencias`, `--com-commit-encerramento`, `--sem-commit-encerramento`) existem nas **duas** bordas; as duas últimas em grupo mutuamente exclusivo (erro de uso, código 2) | presença | Flag ausente em uma das bordas; duas flags exclusivas coexistindo sem erro; divergência de superfície entre CLI e script |
| W007 | `close_flow.py`/`commands/service.py` (024/RF-12, RN-07) | A âncora gravada segue apontando para o último commit de trabalho, inclusive no desfecho não versionado (HEAD e âncora coincidem, sem alerta no `resume`) | redação | Âncora apontando para um commit de encerramento; alerta de divergência no `resume` após fechamento não versionado |
| W008 | `close_flow.py` (024/RN-06/D-05) | Encerrar com `--com-pendencias` (ou `s` no terminal) grava "Sessão encerrada com N mudança(s) não commitada(s) por escolha do usuário" na narrativa | presença | Linha ausente; trabalho pendente autorizado sem rastro na narrativa |
| W009 | `adapters/mcp/server.py` (024/D-04) | A borda MCP mantém `versionar_estado=True` (default), sem pergunta; a assimetria está declarada no docstring | ausência | Flag/pergunta de consentimento propagada ao MCP; fechamento via MCP deixando de versionar silenciosamente |
| W010 | `config.py` + SKILL.md ×3 (024/D-09) | Core em 2.2.0 e skill `encerrar-sessao` em 1.4.0 nas três cópias, com conteúdo idêntico; `SKILL.md` sem promessa de commit automático | presença | Versões cruzadas na base instalada; cópias do `SKILL.md` divergentes; `description` prometendo commit automático |

## Observações (sem peso de regressão)

- O único conflito 🟢 do legado (RN-N31 — encerramento versiona o estado
  incondicionalmente) é **dívida assumida** (achado A001): a re-extração dirigida
  pós-implementação deve reescrever a RN-N31 como condicional ao aval e incorporar
  a `MD-0017`, os ADRs pertinentes, o marker `ENCERRAMENTO_NAO_VERSIONADO` e as
  flags à `domain.md`/`state-machines.md`/`erd`/`code-analysis`. Enquanto isso não
  ocorrer, uma re-extração que releia o código as-built descreverá o comportamento
  novo, mas o `domain.md` ainda afirmará o antigo — este item vigia essa defasagem.
- Nenhuma regra de origem 🟡/🔴 foi tocada; todos os itens acima derivam de
  decisões 🟢 verificadas em código e em smoke real nesta sessão.
- **T028 (propagação à base instalada) não foi executado** — `upgrade`/`migrate`
  nos projetos-alvo e no core-raiz de `~/dev` seguem pendentes (operação manual,
  fora deste repo). Até lá, a base instalada mantém a skill 1.3.0 e o core 2.1.1
  com o comportamento antigo; W010 vigia as versões cruzadas durante a propagação.

## Histórico de re-extrações

_(vazio — primeira geração; a re-extração dirigida pós-024 preencherá esta seção)_

## Arquivadas

_(vazio)_
