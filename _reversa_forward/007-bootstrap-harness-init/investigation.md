# Investigation: Mecanismo de Inicialização e Evolução de Core Local

> Identificador: `007-bootstrap-harness-init`
> Data: `2026-06-24`

Este documento consolida a investigação sobre alternativas de design para provisionamento de cópias locais (módulo per-projeto) e gestão de atualizações do núcleo `harness-core` nos repositórios clientes.

## 1. Alternativas de Provisionamento do Core no Destino

Analisamos três opções principais para disponibilizar o `harness-core` em novos projetos, avaliando-as frente às diretrizes de isolamento e longevidade:

### Opção 1: Links Simbólicos (Symlinks)
Cria links de arquivos e pastas no projeto de destino apontando de volta para a pasta de origem no host local do desenvolvedor.
* **Prós:** Consumo de espaço zero em disco; atualizações feitas no repositório original propagam-se instantaneamente para todos os projetos clientes.
* **Contras:** 
  * Acoplamento espacial crítico: se o repositório original do harness for renomeado, movido ou excluído, todos os projetos de destino quebram instantaneamente.
  * Inconsistência no versionamento Git: o core do harness não é versionado nos projetos clientes. Se outro desenvolvedor clonar o projeto de destino, ele receberá links quebrados e o projeto não funcionará.
  * Violação do Princípio Per-Projeto (MD-0005): a cópia local perde sua característica de independência.

### Opção 2: Git Submodules
Configura a pasta `harness-core/` do destino como um submódulo Git apontando para o repositório original.
* **Prós:** Mantém o histórico do git limpo; permite atualizar com comandos Git padronizados (`git submodule update`).
* **Contras:** Submódulos Git têm uma curva de aprendizado íngreme e causam fricção comum no fluxo diário de commits/pulls dos desenvolvedores. Além disso, exige que o projeto de destino seja obrigatoriamente um repositório git com acesso remoto configurado, limitando ambientes offline ou monorepos informais.

### Opção 3: Cópia Física Completa (Módulo Per-Projeto Autocontido) - ESCOLHIDA
Copia de forma recursiva os arquivos de código-fonte de `harness-core/` (src/, tests/, requirements.txt, harness.toml) e o wrapper Bash `harness` para a raiz do destino.
* **Prós:** 
  * Isolamento absoluto: o projeto de destino torna-se independente do repositório original.
  * Versionado nativamente no Git do destino: qualquer pessoa que clonar o projeto cliente receberá uma cópia funcional do harness.
  * Alinhamento total com as especificações do Reversa e MD-0005 (footprint global zero).
* **Contras:** Pequeno consumo de espaço em disco (~50KB de código Python puro, excluindo venv e caches) e o problema do drift de versão (resolvido na seção abaixo).

---

## 2. Abordagem de Upgrade e Sincronização de Core

Ao escolher a Cópia Física Completa, assumimos a responsabilidade de gerenciar atualizações de versão de forma manual/assistida para evitar obsolescência técnica.

### 2.1 Armazenamento do Rastro do Upstream
O instalador Python (`./harness init`) gravará o metadado `upstream_path` no destino. 
* Se a inicialização for executada via `./harness init /Users/iagoleal/dev/outro-projeto` a partir de `/Users/iagoleal/dev/harness`, o arquivo `harness.toml` (ou setup.json) no destino será gravado com:
  ```toml
  [harness]
  active_harness = "claude"
  upstream_path = "/Users/iagoleal/dev/harness"
  version = "1.2.43"
  ```

### 2.2 Verificação Passiva de Versão
No boot do CLI (`main.py`) ou na inicialização do servidor MCP (`server.py`), o core local lerá o arquivo `harness.toml` do upstream configurado se ele estiver acessível na máquina local.
* Para evitar perda de performance (slowdown no boot do agente), a verificação de versão será baseada em leitura direta do arquivo de configuração do upstream (sem chamadas de subprocesso ou git), rodando apenas se o caminho do diretório estiver acessível no sistema de arquivos local (`os.path.exists(upstream_path)`).

### 2.3 Execução do Upgrade Não Destrutivo
Ao rodar `./harness upgrade` no destino, a lógica fará:
1. Validar se o `upstream_path` existe e contém um core válido.
2. Ler a versão do upstream. Se for igual ou menor à local, aborta informando que já está atualizado.
3. Copiar os arquivos atualizados de `harness-core/src/` e `harness-core/tests/` do upstream para as mesmas subpastas no destino, aplicando um filtro rigoroso de exclusão (ignora arquivos `.venv/`, `.pytest_cache/`, `__pycache__/` e arquivos locais de dados `.toml`/`.json` que possam ter configurações do usuário).
4. Sobrescrever o wrapper executável `harness` na raiz do destino.
5. Preservar as pastas de dados locais (`.harness/` e `.reversa/`) intocadas para que decisões e históricos do projeto cliente nunca sejam corrompidos.
6. Re-executar o bootstrap de ganchos git locais e validação de dependências.

---

## 3. Padrões de Implementação Aplicáveis

* **Strategy Pattern para Cópia Recursiva:** Usaremos cópia recursiva com filtros baseados em expressões regulares ou listas de exclusão estáticas (`shutil.copy2` combinada com funções de filtro customizadas).
* **Command Pattern na CLI:** Encapsularemos as rotas de `init` e `upgrade` em novos comandos do argparse do `main.py`, roteando o controle para o `BootstrapService` estendido.
* **Inversão de Dependência (Ports/Adapters):** A execução de comandos subprocesso (venv e git bootstrap no destino) usará a interface de `ProcessPort` do domínio, mantendo a testabilidade via dublês de teste nos arquivos de testes do pytest.
