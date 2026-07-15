# Investigation: 023-granularidade-lembrete-gate

> Data: `2026-07-15`
> Toda a pesquisa foi interna (código e artefatos do próprio repo); não houve fontes externas a consultar.

## 1. Diagnóstico da queixa

Queixa original: "cada mudança de arquivo está rodando o hook? está ficando muito frequente e atrapalhando o andamento dos processos."

Cadeia de verificação executada nesta sessão:

1. **Varredura por hooks por-edição**: `grep PostToolUse` em `~/dev/*/.claude/settings.json` → zero ocorrências. O format-on-edit foi aposentado na MD-0014 e não sobrou nenhum na base instalada. Neste repo só existem `SessionStart` (resume) e `Stop` (`harness decisions --gate`, timeout 10 s).
2. **Leitura do avaliador** (`core/decisions/gate.py`): `compute_fingerprint(anchor, head, dirty) = sha1(âncora + HEAD + sujos ordenados)`. O docstring declara a intenção: "mudança nova → o gate volta a valer". Comportamento projetado (022/D-03), não bug de implementação.
3. **Leitura da borda** (`main.py`, ramo `--gate`, linhas 341-382): soft-block emitido quando `pendente` e `session.gate_lembrete_fingerprint != verdict.fingerprint`; o fingerprint novo é persistido antes de bloquear. Como cada arquivo novo tocado altera o conjunto sujo, o fingerprint muda a cada turno de trabalho ativo → um bloqueio por arquivo, na prática.
4. **Confirmação empírica**: o próprio soft-block disparou nesta sessão após a criação do `requirements.md` da 023 — dois arquivos novos, fingerprint novo, bloqueio novo.
5. **Confirmação do mantenedor** (clarify, resposta 1a): o incômodo é exatamente esse soft-block repetido.

## 2. Descoberta estrutural decisiva

O fingerprint fino serve a **dois consumidores com necessidades opostas**:

- **Lembrete** (`decisions --gate`): quer ser raro — a finura é o defeito.
- **3º portão do encerramento** (`close_flow.py:376-388`): quer ser fino — se o estado não mudou desde o último bloqueio, o anti-loop libera com aviso (para não travar o usuário em loop infinito); se o usuário fez trabalho novo sem ficha, o fingerprint muda e o portão **deve** bloquear de novo. Engrossar essa identidade enfraqueceria a garantia dura.

Logo a correção não é "consertar o fingerprint", e sim **dar a cada consumidor a identidade que corresponde à sua semântica**. Essa descoberta descartou a alternativa aparentemente óbvia (mudar `compute_fingerprint` na origem) e definiu o D-01 do roadmap.

## 3. Alternativas de política avaliadas (clarify de 2026-07-15)

| Opção | Descrição | Veredito | Porquê |
|-------|-----------|----------|--------|
| (a) | Lembrete único por sessão; identidade = âncora | **adotada** | Espelha a definição de pendência que o portão já usa (ficha desde a âncora satisfaz a sessão inteira — `gate.py:80-85`); zero estado novo; trivial de lembrar em 12 meses |
| (b) | Rearmar também em novo commit sem ficha (identidade = âncora+HEAD) | descartada | Inventa subgranularidade por commit que o domínio não tem; com a disciplina de commits pequenos do mantenedor, continuaria ruidoso |
| (c) | Carência de N turnos entre lembretes | descartada | Exige contador de turnos — estado com sabor de relógio, que a 022 evitou deliberadamente ("sem relógio", D-03); N arbitrário para calibrar |
| (d) | Remover o lembrete; só o portão | descartada | Reverte o enforcement híbrido decidido pelo mantenedor na 022 (esclarecimento 2c); perde o aviso com contexto fresco; escopo além da queixa |

## 4. Padrões e precedentes internos aplicáveis

- **RF-08 da 022 (reconciliado)**: o hook Stop do perfil Claude não tem canal não-bloqueante que alcance o modelo — por isso o lembrete é soft-block; esta feature não reabre esse ponto, só a frequência.
- **RN-N26**: no Antigravity o gate é advisory em stderr, nunca bloqueante — fora do escopo.
- **Padrão de retrocompatibilidade das 021/022**: campos opcionais no estado, tomls sem campo herdam default; aqui nem isso é preciso (D-03, campo reutilizado).
- **Lição da memória "upgrade regrava materializadores stale"**: verificado que nenhum materializador muda nesta feature (hook command idêntico), então não há artefato a regenerar além do bump de versão.

## 5. Pontos verificados que NÃO precisam mudar

- `close_flow.py` — 3º portão (guardado por teste novo, D-06).
- `hook_bridge.py` — advisory Antigravity.
- `ClaudeProfile.hooks_block()` / `.claude/settings.json` — comando do hook inalterado.
- Formato do stdout do `--gate` e textos de help — byte-idênticos.
