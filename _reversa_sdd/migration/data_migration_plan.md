---
schemaVersion: 1
generatedAt: 2026-06-23T14:20:00Z
reversa:
  version: "1.2.43"
kind: data_migration_plan
producedBy: designer
hash: "sha256:c0b80a00492f37752a00827dda0dd5d5a115f4826cbac0be5333ecf228ce9984"
---

# Data Migration Plan

> Plano de migração dos dados do legado para o sistema novo: mapeamento, transformações e validação de qualidade das microdecisões e comandos.

## Resumo
- **Volume estimado**: 17 arquivos Markdown de microdecisões (`MD-0001.md` a `MD-0017.md`), 4 arquivos Markdown de comandos.
- **Janela de migração**: Durante os passos 1 e 2 do cutover (ver `cutover_plan.md`).
- **Estratégia**: Bulk único (cópia física dos arquivos com normalização automatizada de metadados pelo compilador).

## Mapeamento legado → novo

| Origem | Destino | Tipo | Notas |
|---|---|---|---|
| `harness-config/decisoes/MD-*.md` | `decisoes/MD-*.md` | renomeação e carga | Cópia dos arquivos com injeção estruturada de metadados (Front-matter). |
| `harness-config/commands/*.md` | `commands/*.md` | cópia direta | Portados sem alterações sintáticas, adaptados apenas em tempo de prompt. |

## Transformações

### Transformação T-01: Injeção de Front-matter YAML
- **Aplica em**: Cabeçalho de metadados de cada arquivo `decisoes/MD-*.md`.
- **Regra**: O script lê a notação textual legada (ex: `**gancho**: pre-commit`) e a converte no bloco YAML Front-matter padrão delimitado por `---` no topo do arquivo.
- **Tratamento de inválidos**: Rejeitar a migração do arquivo e notificar erro caso os campos obrigatórios (`id`, `gancho`) não sejam identificados no texto legado.
- **Origem da regra**: `target_business_rules.md § BR-MIGRAR-010` e `BR-MIGRAR-011`.

## Estratégia de ETL

- **Ferramenta**: Script de utilitário Python incorporado na CLI nova (`main.py import-legacy <caminho>`).
- **Fluxo**:
  1. **Extração**: Varre o diretório `harness-config/decisoes/` carregando os arquivos Markdown.
  2. **Transformação**: Executa Regex para extrair metadados e monta o cabeçalho YAML Front-matter.
  3. **Carga**: Grava os novos arquivos no diretório alvo do novo repositório.
- **Idempotência**: O processo é destrutivo no diretório temporário de destino, permitindo reexecução infinita a partir da origem legada.
- **Throughput esperado**: Instantâneo (sub-segundo para ~20 arquivos).

## Backfill e delta
- Não aplicável para dados baseados em arquivos locais estáticos sem banco de dados transacional.

## Cutover de dados

- **Janela**: Integrado à janela do plano de cutover geral (`cutover_plan.md`).
- **Sequência de corte**:
  1. Bloquear novas edições no diretório `harness-config/decisoes/`.
  2. Executar `main.py import-legacy` apontando para o diretório legado.
- **Verificação pós-corte**:
  - **Contagens**: O total de arquivos importados em `decisoes/` deve ser exatamente igual a 17.
  - **Validação de Grafo**: Rodar o analisador `DecisionService.validate_integrity()` contra os arquivos importados (deve retornar sucesso com zero órfãos ou referências de backlinks inválidas).

## Validação de qualidade

| Métrica | Alvo | Fonte de medição |
|---|---|---|
| Contagem por entidade | igual a 17 | Verificação de contagem de arquivos no diretório de destino |
| Integridade referencial | 0 órfãos | `DecisionService.validate_integrity()` |
| Validez de Front-matter | 100% dos arquivos com YAML válido | Parser YAML da biblioteca `PyYAML` no carregamento |

## Riscos específicos de dados
- **RISK-003 (Divergência de parsing)**: Ver `risk_register.md`. Riscos de formatação inadequada de metadados que possam quebrar a validação de integridade.

## Notas
A automação da importação em bulk único garante que a transição de dados de microdecisões seja 100% reproduzível, permitindo recriar o ambiente novo a qualquer momento a partir dos dados do repositório legado.
