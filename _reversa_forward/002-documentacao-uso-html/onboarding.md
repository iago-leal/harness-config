# Onboarding: Documentação de Uso Autogerada em HTML

> Identificador: `002-documentacao-uso-html`
> Data: `2026-06-23`
> Roadmap: `_reversa_forward/002-documentacao-uso-html/roadmap.md`

Este guia fornece o passo a passo necessário para testar e validar localmente o gerador de documentação e o servidor HTTP embutido da CLI `harness`.

## Pré-requisitos

1. Certifique-se de que a venv do Python está ativa e as dependências instaladas.
2. Certifique-se de que existem os arquivos gerados pela pipeline reversa (`_reversa_sdd/domain.md`, `_reversa_sdd/architecture.md` e `.reversa/state.json`).

## Passo a Passo para Validação

### Passo 1: Geração da Documentação

Na raiz do projeto, execute o comando de geração do HTML:

```bash
./harness doc-gen
```

**Verificação:**
- Um novo arquivo chamado `harness-docs.html` deve ter sido criado na raiz do projeto.
- Abra o arquivo `harness-docs.html` diretamente no seu navegador abrindo por arquivo local (sem conexão) e verifique:
  - O visual dark mode premium e layout responsivo.
  - A presença da lista de comandos obtida programaticamente da CLI (ex: `bootstrap`, `format`, `decisions`, `cmd`, `doc-gen`, `doc-serve`).
  - O painel com o progresso dos checkpoints do Reversa extraído do `state.json`.

### Passo 2: Servindo a Documentação Localmente

No terminal, execute o comando para expor a documentação gerada em um servidor local:

```bash
./harness doc-serve
```

**Verificação:**
- O console do terminal deve imprimir uma mensagem como `Servidor iniciado em http://localhost:8000`.
- Acesse `http://localhost:8000` em seu navegador.
- Confirme que o HTML de documentação `harness-docs.html` é carregado perfeitamente.
- Pressione `Ctrl+C` no terminal e valide que o servidor é interrompido de forma limpa sem erros na CLI.
