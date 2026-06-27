# Contrato: `cmd regen` + seção `[regen]` do `harness.toml`

> Identificador: `016-encerrar-sessao-autonomo`
> Tipo: CLI + arquivo de configuração

## 1. Configuração (`harness.toml`)

```toml
[regen]
command = "python gerar_site.py && python empacotar.py"
```

- `command`: `Optional[str]`, default `None`. Comando de shell que regenera os artefatos derivados do projeto.
- Mapeado em `HarnessConfig.regen.command` (`src/core/domain/config.py`), via única tipada (RN-N16). Arquivo/seção ausente → `None`.

## 2. CLI — `./harness cmd regen`

| Aspecto               | Valor                                                              |
| --------------------- | ------------------------------------------------------------------ |
| Invocação             | `./harness cmd regen`                                              |
| Entrada               | `harness.toml` (lido por `load_config`); cwd = raiz do projeto     |
| Execução              | `ProcessPort.run_command(["sh", "-c", command], cwd=repo_path)`    |
| Saída (sucesso)       | stdout/stderr do comando repassados; exit 0                        |
| Saída (regen ausente) | mensagem "nenhum comando de regen configurado"; **exit 0** (no-op) |
| Saída (regen falho)   | exit ≠ 0 + mensagem barulhenta com o código e o stderr do comando  |
| Idempotência          | delegada ao comando do projeto (o harness só dispara)              |
| Timeout               | n/a no MVP (o comando do projeto governa); reavaliar se necessário |

## 3. Posição no fluxo "faz tudo"

A skill `.md` sequencia: `cmd regen` → `cmd encerrar-sessao`. O `regen` roda **primeiro**, produzindo os derivados; em seguida o `encerrar-sessao` faz o pré-check da working tree (marker `COMMIT_PENDENTE`) e fecha. Se `regen` falhar (exit ≠ 0), a sequência **não** chega ao fechamento (D2: abortar sem fechar, sem rollback, re-executável).

## 4. Fronteiras de responsabilidade

- O core **não conhece** o que cada projeto regenera (baixo acoplamento, RN-N5): só executa o comando declarado.
- `RegenService` (novo, `src/core/regen/service.py`) depende apenas do `ProcessPort` (porta), não de git nem de fs de domínio.
- Sem `git add` aqui: versionar o que o regen produziu é decisão do agente no passo do `COMMIT_PENDENTE` (ou via `.gitignore`).

## 5. Segurança

O comando roda com os privilégios do usuário e é declarado pelo próprio dono do projeto (mesma confiança de um script de build). O harness não injeta entrada externa no comando. Escrita esperada apenas sob a raiz do projeto.
