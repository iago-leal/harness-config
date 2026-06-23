# language: pt
# spec-id: PT-001
# rastreabilidade:
#   process_flows: _reversa_sdd/sync-check/requirements.md
#   target_architecture: SyncService, SyncCache
#   paradigma_alvo: Orientação a Objetos com Injeção de Dependências

Funcionalidade: Sincronia de Repositórios Remotos
  Como desenvolvedor ou agente de IA
  Quero verificar a sincronia do repositório local com o remote na inicialização da sessão
  Para garantir que estou trabalhando com o código mais atualizado sem lentidão de rede

  @paridade @critico
  Cenário: Inicialização de sessão com cache expirado dispara consulta Git
    Dado que a última verificação de sincronia no cache do repositório ocorreu há mais de 24 horas
    Quando a checagem de sincronia é executada
    Então o sistema deve consultar a rede utilizando "git ls-remote"
    E deve atualizar o cache local com o timestamp atual e o commit hash do remote

  @paridade @critico
  Cenário: Inicialização de sessão com cache dentro do TTL de 24 horas pula consulta Git
    Dado que a última verificação de sincronia no cache ocorreu há 12 horas
    Quando a checagem de sincronia é executada
    Então o sistema deve pular a consulta de rede "git ls-remote"
    E deve ler o status a partir do cache local sem latência de rede

  @paridade @resiliencia
  Cenário: Falha de conexão de internet ou erro Git não bloqueia a CLI
    Dado que a última verificação de sincronia no cache ocorreu há mais de 24 horas
    E o servidor remoto de Git está offline ou inacessível
    Quando a checagem de sincronia é executada
    Então o sistema deve registrar o erro em logs locais
    E deve retornar status de saída igual a 0, sem interromper o boot do harness
