# Actions: Oferta de commit consentida (fim do commit automático)

> Identificador: `024-oferta-commit-consentida`
> Data: `2026-07-23`
> Roadmap: `_reversa_forward/024-oferta-commit-consentida/roadmap.md`
> **Regeneração** — segunda versão, derivada do roadmap reescrito após a auditoria
> e a segunda clarificação. IDs preservados (T001–T024); as ações nascidas da RN-08
> e da D-08 recebem IDs novos a partir de T025.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 28 |
| Paralelizáveis (`[//]`) | 11 |
| Maior cadeia de dependência | 10 (T001 → T003 → T006 → T014 → T015 → T016 → T020 → T022 → T023 → T028) |

## Fase 1, Preparação

<!-- Sem scaffolding nem migração: a feature não cria módulo novo nem toca schema (data-delta §1). A preparação é de leitura dirigida, para o núcleo não descobrir acoplamento tarde. -->

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Inventariar todo ponto que casa o **texto literal** do campo `acao` do `COMMIT_PENDENTE` (testes das features 016/019, contratos em `_reversa_forward/019-*/interfaces/`, mini-site) e listar o que precisa de ajuste; o formato dos demais campos fica intocado (RF-10) | - | `[//]` | `.harness/harness-core/tests/` | 🟢 | `[X]` |
| T002 | Confirmar por leitura que `close_session` zera `gate_lembrete_fingerprint`/`gate_encerramento_fingerprint` **antes** do ponto onde o commit de encerramento deixa de ocorrer, de modo que o desfecho não versionado também limpe os fingerprints (data-delta §4.3) | - | `[//]` | `.harness/harness-core/src/core/domain/models.py` | 🟢 | `[X]` |

## Fase 2, Testes

<!-- TDD, como nas features 022/023: teste red primeiro, exceto os testes-guarda, que podem nascer verdes para pinar comportamento que NÃO deve mudar. -->

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Teste (red) de `render_commit_pendente_marker`: o campo `acao` passa a descrever a **oferta** (perguntar ao usuário antes de commitar; `--com-pendencias` como saída da recusa); `arquivos`/`total`/`truncado`/`mostrados` e o teto de 20 preservados byte a byte (RF-01/RF-10) | T001 | - | `.harness/harness-core/tests/test_close_flow.py` | 🟢 | `[X]` |
| T004 | Teste (red) de `render_encerramento_nao_versionado_marker`: formato do marker pós-fechamento com `arquivo`, `ancora` (SHA-1 de 40), `motivo` (`sem-autorizacao` \| `recusa-explicita`) e `acao`, conforme `interfaces/encerramento-nao-versionado-marker.md` §3 | T001 | - | `.harness/harness-core/tests/test_close_flow.py` | 🟢 | `[X]` |
| T005 | Teste (red) de `CommandService.execute_command(..., versionar_estado=False)`: grava o estado, **não** chama `commit_paths` e acrescenta a linha declarativa em `narrative.feito` (D-05); mais teste-guarda de que o default `True` mantém intacto o comportamento da RN-N31 | T001 | `[//]` | `.harness/harness-core/tests/test_commands.py` | 🟢 | `[X]` |
| T006 | Teste (red) do pré-check interativo: a saída traz a **contagem** antes da lista e a pergunta de segunda ordem ("encerrar mesmo assim?"); `s` libera o portão, `n` aborta sem fechar e sem commitar (RF-04/RF-06); com lista truncada, a contagem anunciada é o total real (34), não o número de exibidos (20) | T003 | - | `.harness/harness-core/tests/test_close_flow.py` | 🟢 | `[X]` |
| T007 | Teste (red) da pergunta do commit de encerramento em terminal: default afirmativo `[S/n]` (D-07); resposta negativa fecha o estado, não cria commit e emite o marker com `motivo=recusa-explicita` (RF-07/RN-07); mais o cenário de **árvore limpa**, em que o fluxo pula a oferta de commit do trabalho e vai direto a esta decisão | T004 | - | `.harness/harness-core/tests/test_close_flow.py` | 🟢 | `[X]` |
| T008 | Teste (red) da **matriz de resolução sem terminal** (`interfaces/flags-encerramento.md` §3): sem flag → não versiona e emite o marker com `motivo=sem-autorizacao`; `--com-commit-encerramento` → versiona sem marker; `--sem-commit-encerramento` → idêntico ao default; `--com-pendencias` libera o 1º portão; nenhum caminho chama `input()` sem TTY (RF-08). Assertar também a **ordem** exigida pelo contrato: o marker sai depois da mensagem de sucesso e antes da oferta de push | T003, T004 | `[//]` | `.harness/harness-core/tests/test_cli.py` | 🟢 | `[X]` |
| T009 | Teste (red) de **duas sessões encadeadas** após fechamento não versionado: o `state_file` sujo não dispara o pré-check (excluído por caminho exato), a âncora coincide com o HEAD, o `resume` não alerta divergência e o gate de decisões (022) não é confundido pela árvore suja — o `state_file` já é excluído do universo do gate em `gate.py:84-85` (data-delta §4.2, roadmap §9) | T005 | - | `.harness/harness-core/tests/test_close_flow.py` | 🟢 | `[X]` |
| T010 | Testes-guarda (podem nascer verdes) dos portões 2 e 3: gate de narrativa viva e gate de registro de decisões seguem com gatilho, anti-loop e escape `--sem-decisao` inalterados; nenhuma flag nova interfere neles | T003 | - | `.harness/harness-core/tests/test_close_flow.py` | 🟢 | `[X]` |
| T025 | Teste (red) do **grupo mutuamente exclusivo** (D-08): `--com-commit-encerramento` junto de `--sem-commit-encerramento` produz erro de uso do `argparse`, código de saída 2 e nenhum efeito sobre a sessão, nas duas bordas | T008 | - | `.harness/harness-core/tests/test_cli.py` | 🟢 | `[X]` |
| T026 | Teste (red) da precedência **flag vence pergunta**: em terminal interativo, com qualquer das duas flags de encerramento, o `asker` não é chamado para essa decisão e o desfecho é o da flag (`interfaces/flags-encerramento.md` §3, regra derivada 1) | T007 | - | `.harness/harness-core/tests/test_close_flow.py` | 🟢 | `[X]` |
| T027 | Teste (red) da linha declarativa de pendências autorizadas: encerrar com `--com-pendencias` (ou `s` no terminal) grava em `narrative.feito` a declaração "Sessão encerrada com N mudança(s) não commitada(s) por escolha do usuário" (data-delta §3) | T006 | - | `.harness/harness-core/tests/test_close_flow.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T011 | Reescrever o campo `acao` de `render_commit_pendente_marker` para o texto de oferta do contrato, sem tocar na montagem dos demais campos. Torna T003 verde | T003 | - | `.harness/harness-core/src/core/session/close_flow.py` | 🟢 | `[X]` |
| T012 | Implementar `render_encerramento_nao_versionado_marker(state_file, ancora, motivo)` e exportá-la em `__all__`, conforme o contrato novo. Torna T004 verde | T004 | - | `.harness/harness-core/src/core/session/close_flow.py` | 🟢 | `[X]` |
| T013 | Adicionar `versionar_estado: bool = True` a `execute_command`: quando falso, salvar o estado, pular `commit_paths`, acrescentar a linha declarativa na narrativa e devolver mensagem que diz o que ficou pendente. O default preserva todos os chamadores, inclusive o MCP (D-03/D-04). Torna T005 verde | T002, T005 | `[//]` | `.harness/harness-core/src/core/commands/service.py` | 🟢 | `[X]` |
| T014 | Reescrever `conduct_commit_pendente`: no modo interativo, anunciar a contagem, listar os caminhos e perguntar o desfecho pelo `asker` (D-02), devolvendo a autorização ao chamador; sem terminal, seguir emitindo o marker. A função continua sem executar `git add` (RN-N5). Torna T006 verde | T006, T011 | - | `.harness/harness-core/src/core/session/close_flow.py` | 🟢 | `[X]` |
| T015 | Estender `SessionCloseFlow.run` com `com_pendencias: bool` e `versionar_encerramento: Optional[bool]` (tri-estado): resolver o default por borda (terminal pergunta `[S/n]`; sem terminal, `None` vale recusa — RN-08), fazer a flag vencer a pergunta, liberar o 1º portão quando autorizado e gravar a declaração das pendências, repassar `versionar_estado` ao `CommandService` e emitir o marker pós-fechamento com o `motivo` correto e com a âncora obtida por `get_head_commit` **antes** do fechamento (D-11). Torna T007, T008, T009, T026 e T027 verdes | T007, T009, T012, T013, T014, T026, T027 | - | `.harness/harness-core/src/core/session/close_flow.py` | 🟢 | `[X]` |

## Fase 4, Integração

<!-- Todas dependem do núcleo pronto (T015) e tocam arquivos distintos entre si. -->

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T016 | Adicionar ao subparser `cmd` da CLI a flag `--com-pendencias` e o grupo mutuamente exclusivo `--com-commit-encerramento` / `--sem-commit-encerramento`, repassando-as ao `SessionCloseFlow.run` ao lado do `--sem-decisao` já existente. Torna T025 verde na borda CLI | T015, T025 | `[//]` | `.harness/harness-core/src/main.py` | 🟢 | `[X]` |
| T017 | Adicionar as mesmas três flags, com o mesmo grupo exclusivo, ao script fino da skill e repassá-las ao mesmo fluxo, mantendo a paridade de superfície exigida pela RN-N33 | T015 | `[//]` | `.claude/skills/encerrar-sessao/scripts/encerrar_sessao.py` | 🟢 | `[X]` |
| T018 | Reescrever o `SKILL.md` nas **três** cópias (`.claude/`, `.agents/`, `src/core/install/assets/skills/`): passo 3 vira "pergunte antes de commitar", passo novo para a decisão do commit de encerramento, para as flags e para o marker `ENCERRAMENTO_NAO_VERSIONADO` (incluindo a reação distinta por `motivo`), `description` do front-matter sem a promessa de commit automático, `version` 1.3.0 → 1.4.0 (D-09) | T015 | `[//]` | `.claude/skills/encerrar-sessao/SKILL.md` (+2 cópias) | 🟢 | `[X]` |
| T019 | Teste-guarda do adaptador MCP: segue chamando `execute_command` sem a flag e portanto versionando o estado, sem pergunta (D-04); registrar a assimetria no docstring do adaptador | T015 | `[//]` | `.harness/harness-core/src/adapters/mcp/server.py` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T020 | Escrever os textos de `--help` das três flags dizendo a **consequência**, não o efeito mecânico, idênticos nas duas bordas (`interfaces/flags-encerramento.md` §6) | T016, T017 | - | `.harness/harness-core/src/main.py` + script fino da skill | 🟢 | `[X]` |
| T021 | Bump do core 2.1.1 → 2.2.0 (minor, D-09) e verificação de que o `hook command` do Stop não muda — o gate da 022 é ortogonal a esta feature | T015 | `[//]` | `.harness/harness-core/src/core/domain/config.py` | 🟢 | `[X]` |
| T022 | Rodar a suíte completa: casos novos verdes, testes-guarda verdes e zero regressão nas features 013/014/016/018/019/022/023 | T016, T017, T018, T019, T020, T021 | - | `.harness/harness-core/tests/` | 🟢 | `[X]` |
| T023 | Smoke manual com **git real** num repositório descartável, cobrindo os cenários A a G do `onboarding.md`, com atenção ao E (default invertido) e ao G (duas sessões encadeadas) — mock de git esconde o colapso do porcelain em subpasta não rastreada (lição da feature 019) | T022 | - | manual (repositório temporário) | 🟢 | `[X]` |
| T024 | Registrar a ficha `MD-0017` (política de consentimento para escrita no git ao encerrar: dois pontos de decisão, default assimétrico por borda, flags como canal sem terminal, inversão deliberada da RN-N31 e alternativas descartadas do `investigation.md` §4) e regenerar o índice via `./harness decisions` | T015 | `[//]` | `.harness/decisoes/MD-0017.md` | 🟢 | `[X]` |
| T028 | Propagar à base instalada (roadmap §8.5): `upgrade`/`migrate` nos projetos-alvo e o core-raiz de `~/dev` via `.harness/upgrade-raiz.sh`, conferindo que os materializadores regravaram o `SKILL.md` 1.4.0 e as flags novas | T023 | - | manual (projetos-alvo, fora deste repo) | 🟢 | `[ ]` |

## Notas de execução

<!-- Reservado para /reversa-coding. -->

- **Nome das flags:** vale o par `--com-commit-encerramento` / `--sem-commit-encerramento`,
  uniforme desde o saneamento do achado A011 — D-01, D-10, contrato,
  `onboarding.md` e este documento dizem o mesmo.
- Ao executar T018, as três cópias do `SKILL.md` precisam ficar idênticas no
  conteúdo relevante; divergência entre elas já causou bug de materializador
  stale na base instalada (memória do projeto).
- T023 e T028 exigem execução manual com `!` — o modo automático bloqueia
  comandos que operam fora do repositório.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-07-23 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-07-23 | Regeneração sobre o roadmap reescrito: terminologia "commit de encerramento", marker e renderizador renomeados, `versionar_encerramento` tri-estado, três flags com grupo exclusivo; T025–T028 novos; alvo do bump corrigido para `domain/config.py` | reversa |
| 2026-07-23 | Saneamento dos achados da segunda auditoria, sem ação nova: T006 ganha o anúncio do total truncado (A009), T007 o cenário de árvore limpa (A010), T008 a ordem do marker (A014), T015 o canal da âncora (A013/D-11), T020 a segunda borda (A008); T009 sobe a 🟢 (A015) | reversa |
