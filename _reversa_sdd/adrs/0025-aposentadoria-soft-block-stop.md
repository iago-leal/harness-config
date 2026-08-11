# ADR 0025: Aposentadoria do soft-block do Stop — enforcement em duas políticas

- **Status:** Aceito
- **Data:** 2026-08-11 (feature 025-aposentar-soft-block-stop, MD-0018; não commitada na data desta extração)
- **Contexto Técnico:** apenas o ramo `decisions --gate` do `main.py` muda: pendência inédita deixa de emitir o JSON `{"decision":"block",...}` no stdout e passa a emitir linha `Aviso:` em stderr; stdout torna-se sempre vazio. `gate.py`, `close_flow.py`, serializer e modelos byte-idênticos; `.claude/settings.json` inalterado (mesmo comando no hook Stop). Core 2.2.0 → 2.3.0.
- **Escala de Confiança:** 🟢 CONFIRMADO (diff de escopo negativo conferido; suíte verde).
- **Decisões relacionadas:** MD-0018 (`substitui MD-0016`, `refina MD-0015`); ADR 0022 (o gate), ADR 0023 (dupla identidade — a identidade grossa sobrevive e segue limitando o aviso a um por sessão); domain.md RN-N44 revisada (§2.23).

## Contexto e Problema

Mesmo após a 023 reduzir o soft-block a no máximo um por sessão, o mantenedor relatou que o projeto seguia "bloqueando o desenvolvimento com muitas pausas". O soft-block do Stop interrompia o turno para exigir uma ficha que o portão do encerramento já garantiria de qualquer forma; o custo (interrupção do fluxo) superava o benefício (registro com contexto fresco). O Antigravity, que sempre teve só aviso, nunca gerou queixa equivalente — evidência de que o aviso basta.

## Decisão

**Despromover o lembrete do Stop de soft-block a advisory puro e concentrar toda a garantia dura no único momento em que ela é barata: o encerramento.** O enforcement colapsa de três políticas para duas: (1) portão bloqueante único, o 3º portão do `encerrar-sessao` (identidade fina, anti-loop, escape `--sem-decisao` — mecânica 022/023 intacta); (2) advisory nos fins de turno, agora idêntico em espírito nas duas bordas ("o Claude convergiu para a política que o Antigravity já tinha").

Toda a mecânica do ramo `--gate` sobrevive: avaliação pura, persistência da identidade grossa **antes** da emissão (máximo um aviso por sessão), reindexação, fail-open, exit 0. Muda apenas o canal e a forma do desfecho: stderr `Aviso:` em vez de stdout JSON. Nenhum arquivo de hook é regravado — a mudança é comportamental no comando, propagada à base migrada pela fonte única (RN-N36).

## Alternativas Consideradas

- **Remover o hook Stop do `settings.json`:** descartado — perderia o aviso com contexto fresco e exigiria regravar hooks na base instalada; o comando advisory mantém o valor sem o atrito.
- **Flag de política no toml (block vs advise):** descartado — YAGNI, mesma lógica do ADR 0023; a experiência mostrou que o block não se sustenta nem como opção.
- **Aumentar a carência (avisar só após N turnos):** descartado — contador com sabor de relógio, já rejeitado na 022/023.
- **Aposentar também o aviso:** descartado — o aviso é gratuito e preserva a chance de registrar com contexto fresco.

## Consequências

- **Positivas:**
  - Zero interrupções de turno; a garantia de registro permanece integral no portão do encerramento (pinado por teste desde a 023).
  - Convergência entre bordas: Claude e Antigravity passam a ter a mesma política de fim de turno.
  - Propagação automática pela fonte única; nenhum hook regravado, nenhuma migração.
- **Negativas / em aberto:**
  - O registro com contexto fresco vira responsabilidade do agente/mantenedor ao ler o aviso; nada mais força a pausa.
  - MD-0016 (dupla identidade) fica **substituída** na política, embora a identidade grossa continue em uso como limitador do aviso — a relação `substitui` registra a mudança de finalidade, não a remoção do mecanismo.
