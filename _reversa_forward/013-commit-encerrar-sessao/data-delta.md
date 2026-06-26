# Data Delta: Versionar o estado da sessão ao encerrar

> Identificador: `013-commit-encerrar-sessao`
> Data: `2026-06-26`
> Base extraída: `_reversa_sdd/session/requirements.md`, `_reversa_sdd/domain.md#2.3`

## 1. Veredito

**Nenhuma mudança de schema.** O modelo `SessionState`/`SessionNarrative`
(`src/core/domain/models.py`) e o formato do artefato `.harness/estado-da-sessao.md`
(front-matter YAML + corpo Markdown, RN-N1/RN-N2) permanecem **idênticos**. A feature
altera o **ciclo de vida git** do arquivo, não o seu conteúdo nem sua estrutura.

## 2. Campos

| Campo                  | Antes                               | Depois    | Observação                                                                                         |
| ---------------------- | ----------------------------------- | --------- | -------------------------------------------------------------------------------------------------- |
| `commit_hash` (âncora) | SHA-1 do HEAD gravado no fechamento | **igual** | Continua sendo o último commit de **trabalho**, capturado antes do commit de encerramento (RN-03). |
| `active_feature`       | nome da feature ativa               | **igual** | Usado também na mensagem do commit de encerramento (D-06).                                         |
| `is_active`            | vai a `false` no fechamento         | **igual** | `close_session` inalterado.                                                                        |
| narrativa (corpo)      | 4 seções fixas                      | **igual** | Round-trip preservado (RN-N2).                                                                     |

- Novos campos: **nenhum**.
- Campos removidos: **nenhum**.
- Validações alteradas: **nenhuma** (`validate_commit_hash` intacto).

## 3. Mudança de ciclo de vida (não é schema)

O que muda é o estado do arquivo perante o git:

| Momento                | Antes                                                                            | Depois                                                                          |
| ---------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Após `encerrar-sessao` | `.harness/estado-da-sessao.md` fica **modificado/não commitado** no working tree | arquivo **commitado** num commit dedicado por cima do último commit de trabalho |
| Histórico git          | sem registro do fechamento                                                       | commit `chore(sessao): encerrar sessão <feature>; âncora <ancora>`              |
| Working tree           | sujo (registro pendente, fácil de esquecer)                                      | limpo quanto ao `state_file`; mudanças alheias permanecem intocadas             |

## 4. Migrações necessárias

- **Migração de dados:** n/a. Nenhuma transformação de artefatos existentes; estados
  `.harness/estado-da-sessao.md` já gravados continuam válidos sem conversão.
- **Migração operacional:** bump de versão 1.2.48 → 1.2.49 e rematerialização dos slash
  commands (ver `roadmap.md` D-08 e plano de migração) — necessária para o texto exibido,
  não para os dados.
- **Compatibilidade retroativa:** total. Um repositório onde o arquivo de estado já
  estava pendente antes da feature simplesmente passa a tê-lo commitado no próximo
  `encerrar-sessao`.

## 5. Índices / armazenamento

- n/a. Não há banco de dados nem índices; a persistência é em arquivo versionado por git.
