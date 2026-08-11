# Contrato: CLI `harness progress`

> Identificador: `026-medidor-progresso-entregaveis`
> Data: `2026-08-11`
> Tipo: contrato de processo (argumentos, stdout/stderr, exit codes, formato de arquivo)

## 1. Invocação

```
harness progress             # modo padrão: (re)grava .harness/progresso.md
harness progress --json      # medição crua no stdout, para máquina
harness progress --em-hook   # modo pre-commit: reprova só se o arquivo estava defasado
```

`--json` e `--em-hook` são mutuamente exclusivos (erro barulhento do argparse, exit 2). Cwd: raiz do projeto instalado. Sem stdin.

## 2. Modo padrão

- Computa a medição e grava `config.progress.file` (default `.harness/progresso.md`) **apenas se os bytes mudarem**; informa em stdout `progresso.md regravado` ou `progresso.md já estava em dia`.
- Exit 0 com ou sem alertas na medição; exit 2 apenas em falha real de leitura (fonte corrompida/ilegível), com caminho e causa em stderr.
- Fonte legitimamente ausente (sem `.reversa/`, sem sessão, sem regression-watch) não é falha: a seção correspondente sai como `n/a`.

## 3. Formato do markdown (`.harness/progresso.md`)

Regras invariantes: **nenhum timestamp de geração ou valor volátil** (diff só quando o estado muda); listas ordenadas deterministicamente; sem caminhos absolutos da máquina. Seções, nesta ordem:

1. Cabeçalho fixo com aviso "arquivo derivado, não edite" e o comando de regeneração.
2. **Ciclo forward** — feature ativa (id, nome, estágio físico, tabela de ações `[X]`/total por fase), features pausadas (id, estágio de pausa), contagem de features concluídas.
3. **Harness** — sessão (status, âncora abreviada), microdecisões (total de fichas, id da última), pendência de registro do gate (booleano + total de mudanças, sem listar caminhos).
4. **Alertas** — um por linha com severidade (`alta`/`media`); seção presente com "nenhum" quando vazia.

## 4. Modo `--json`

Medição completa no stdout como JSON UTF-8 (`ensure_ascii=False`), incluindo os mesmos números do markdown mais `aferido_em` (ISO 8601, permitido porque stdout não é versionado). Não grava arquivo. Exit 0 (ou 2 em falha real).

## 5. Modo `--em-hook`

Semântica transplantada de `tools/estado.py::_no_hook` (comentarios-concursos):

| Situação | Efeito | exit |
|---|---|---|
| Arquivo em dia com as fontes | nada a fazer | 0 |
| Arquivo defasado | **regrava** e instrui em stderr (`git add .harness/progresso.md && git commit`) | 1 |
| Alertas de severidade alta, arquivo em dia | aviso em stderr, commit passa | 0 |
| Projeto sem `.reversa/` e sem artefato prévio | caso normal de instalação nova | 0 |

Racional: alerta alto não reprova commit — um guardrail que impede a correção do que denuncia é pior que guardrail nenhum. O que reprova é uma coisa só: o arquivo versionado ter deixado de dizer a verdade, e o remédio já vem aplicado. **Nesta feature a flag não é materializada em nenhum hook** (RN-07); a integração ao `bootstrap` é passo futuro.

## 6. Garantias transversais

- Idempotência: mesmas fontes → mesmos bytes (modo padrão) / mesmo JSON exceto `aferido_em`.
- Só-leitura fora do artefato próprio: nenhuma escrita em `.reversa/`, `_reversa_forward/`, `_reversa_sdd/` ou no estado de sessão (o reuso de `evaluate_registration_gate` não persiste fingerprint).
- Determinismo de ordenação: features por id numérico; fases na ordem do `actions.md`; alertas por severidade e depois por origem.

## 7. Consumidores conhecidos

| Consumidor | Uso |
|---|---|
| Mantenedor | Leitura direta do `.harness/progresso.md` versionado; `git log -p` como linha do tempo do progresso |
| Agentes (Claude/Antigravity) | Leitura do arquivo na retomada; `--json` para consumo estruturado |
| Hook futuro do bootstrap | `--em-hook` (fora do escopo da 026) |
