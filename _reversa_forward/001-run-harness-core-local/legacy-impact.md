# Legacy Impact: Execução Local do Harness Core

> Identificador: `001-run-harness-core-local`
> Data: `2026-06-23`

## 1. Mapeamento de Impacto no Legado

Os arquivos criados ou modificados no âmbito desta evolução técnica estão detalhados a seguir:

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
| :--- | :--- | :--- | :--- | :--- |
| `harness` | Interface executável | componente-novo | LOW | Novo script wrapper na raiz para unificar a execução do núcleo Python. |
| `.reversa/settings.json.snippet` | Ganchos do ciclo de vida | regra-alterada | LOW | Configuração alternativa de ganchos em formato de snippet, preservando o arquivo original do legado. |
| `harness-core/tests/test_wrapper.py` | Suite de Testes | componente-novo | LOW | Casos de teste automatizados para validar a execução do wrapper local. |

## 2. Diff Conceitual por Componente

### Interface executável (Núcleo)
A introdução do script `./harness` na raiz estabelece um atalho unificado e independente de rede que invoca a venv local do Python (`harness-core/.venv/bin/python3`) e encaminha parâmetros para `harness-core/src/main.py`. Isso remove o acoplamento do desenvolvedor humano e do agente de IA a caminhos globais do host.

### Ganchos do Ciclo de Vida
Os ganchos do agente local do editor (`SessionStart` e `PostToolUse`) foram redirecionados para chamar o wrapper de entrada `./harness`. Esta alteração está consolidada em formato de snippet isolado em `.reversa/settings.json.snippet` para respeitar a regra não-negociável de não modificação de arquivos de configuração pré-existentes do legado.

## 3. Regras Preservadas

As seguintes regras de domínio confirmadas em `_reversa_sdd/domain.md` foram totalmente preservadas:
* **Verificação Sincronizada em SessionStart (RD-01):** O hook de boot local continua a rodar via redirecionamento ao wrapper.
* **Resiliência Offline (RD-02):** A execução local via Python e shell script independe de rede ou serviços de terceiros.
* **Garantia de Não-Bloqueio de Formatadores (RD-03):** O formatador do núcleo Python silencia seus erros e encerra com código `0`.
* **Consolidação Automática no Fechamento (RD-04):** A compilação e validação do grafo de microdecisões no encerramento da sessão permanecem ativas e automáticas.

## 4. Regras Modificadas

* Nenhuma regra de negócio confirmada do legado foi modificada ou removida de forma destrutiva. Apenas o mecanismo de invocação técnica migrou de scripts Bash globais no `$HOME` para o interpretador local do projeto.
