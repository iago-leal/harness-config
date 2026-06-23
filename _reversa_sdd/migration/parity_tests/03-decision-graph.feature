# language: pt
# spec-id: PT-003
# rastreabilidade:
#   process_flows: _reversa_sdd/microdecisoes/requirements.md
#   target_architecture: DecisionService
#   paradigma_alvo: Orientação a Objetos com Injeção de Dependências

Funcionalidade: Compilação e Grafo de Microdecisões
  Como arquiteto de software ou desenvolvedor
  Quero compilar e validar o índice de microdecisões de design
  Para manter backlinks e integridade referencial consistentes no Git

  @paridade @critico
  Cenário: Parser converte metadados textuais e inverte o grafo bidirecionalmente
    Dado que existe uma microdecisão "decisoes/MD-0002.md" com ID "MD-0002"
    E uma microdecisão "decisoes/MD-0003.md" com a relação "refina MD-0002"
    Quando o DecisionService compila o índice de decisões em "microdecisoes.md"
    Então o arquivo "microdecisoes.md" deve conter a relação direta de "MD-0003 refina MD-0002"
    E deve conter a relação inversa mapeada de "MD-0002 refinado-por MD-0003"

  @paridade @validacao
  Cenário: Rejeição de relações de metadados malformadas
    Dado que existe uma microdecisão com a relação malformada "refina MD-0002 extra-token"
    Quando o DecisionService processa o arquivo
    Então o sistema deve lançar uma exceção de validação de metadados
    E interromper a compilação do índice de microdecisões

  @paridade @pre-commit
  Cenário: Validação de pre-commit rejeita commit com índice defasado
    Dado que existe uma nova microdecisão "decisoes/MD-0018.md" no disco
    E o índice "microdecisoes.md" ainda não foi recompilado para incluí-la
    Quando o gancho Git "pre-commit" executa as validações do core Python
    Então o sistema deve retornar código de erro de validação (diferente de 0)
    E bloquear a submissão do commit até a recompilação do índice
