# language: pt
# spec-id: PT-004
# rastreabilidade:
#   process_flows: _reversa_sdd/comandos-customizados/requirements.md
#   target_architecture: CommandService
#   paradigma_alvo: Orientação a Objetos com Injeção de Dependências

Funcionalidade: Sessão Interativa de Comandos e PCCP
  Como desenvolvedor ou agente de IA
  Quero executar comandos customizados de ciclo de vida de sessão e clarificação
  Para manter o alinhamento de requisitos sem consumir tokens excessivos

  @paridade @critico
  Cenário: Comando de clarificação bloqueia após a segunda rodada de perguntas
    Dado que a funcionalidade de clarificação baseada em PCCP está ativa
    E o diálogo de clarificação entre o usuário e o agente já completou duas rodadas
    Quando o CommandService avalia o estado da interação
    Então o sistema deve impedir novas perguntas e sugerir o travamento de escopo
    E abortar o loop de diálogo para economizar recursos do usuário

  @paridade @sessao
  Cenário: Encerramento de sessão grava o commit HEAD de âncora
    Dado que o repositório Git local possui o commit HEAD com hash "9e7d533a4f4c4d53c83c2ef71036d80a12506e69"
    Quando o comando "/encerrar-sessao" é executado
    Então o sistema deve salvar as pendências locais em commits atômicos
    E gravar o hash de âncora "9e7d533a4f4c4d53c83c2ef71036d80a12506e69" no arquivo "ESTADO-DA-SESSAO.md"
    E travar edições subsequentes na sessão até a retomada pelo comando "/resume"
