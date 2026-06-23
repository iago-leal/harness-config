# language: pt
# spec-id: PT-002
# rastreabilidade:
#   process_flows: _reversa_sdd/format-on-edit/requirements.md
#   target_architecture: FormattingService, FormatterConfig
#   paradigma_alvo: Orientação a Objetos com Injeção de Dependências

Funcionalidade: Formatação Automática ao Gravar Arquivos
  Como desenvolvedor ou agente de IA
  Quero que meus arquivos modificados sejam formatados automaticamente ao salvar
  Para manter o padrão estético do projeto sem travar meu fluxo de escrita

  @paridade @critico
  Cenário: Formatação de arquivo priorizando executáveis locais do projeto
    Dado que um arquivo "src/main.py" foi modificado
    E existe um formatador "ruff" local configurado em ".venv/bin/ruff"
    Quando o formatador é acionado para o arquivo modificado
    Então o sistema deve executar a formatação usando o ruff local de ".venv/bin/ruff"
    E retornar código de saída 0

  @paridade @opt-out
  Cenário: Presença de arquivo no-autoformat na raiz cancela formatação
    Dado que o arquivo ".no-autoformat" está presente na raiz do projeto
    E um arquivo "src/main.py" foi modificado
    Quando o formatador é acionado para o arquivo modificado
    Então o sistema deve ignorar a formatação e manter o arquivo intacto
    E retornar código de saída 0

  @paridade @blindagem
  Cenário: Modificações em diretórios protegidos do sistema não sofrem formatação
    Dado que o arquivo modificado reside sob o diretório do usuário "/Users/iagoleal/.claude/settings.json"
    Quando o formatador é acionado para o arquivo modificado
    Então o sistema deve abortar imediatamente a execução
    E garantir que nenhuma alteração seja feita no arquivo protegido
    E retornar código de saída 0

  @paridade @resiliencia
  Cenário: Erro no binário do formatador não interrompe gravação
    Dado que um arquivo "src/main.py" foi modificado
    E o executável do formatador local falha catastróficamente com código de saída 127
    Quando o formatador é acionado para o arquivo modificado
    Então o sistema deve capturar a exceção e gravá-la nos logs
    E retornar código de saída 0, assegurando o não-bloqueio do ciclo do harness
