# Data Delta: Documentação de Uso Autogerada em HTML

> Identificador: `002-documentacao-uso-html`
> Data: `2026-06-23`
> Roadmap: `_reversa_forward/002-documentacao-uso-html/roadmap.md`

## 1. Alterações no Schema / Modelo Físico

Não aplicável. Esta feature não cria novas tabelas de banco de dados, nem adiciona esquemas SQL/NoSQL novos ao núcleo do `harness`. 

## 2. Estrutura de Leitura de Arquivos de Estado

O serviço lê arquivos JSON e Markdown locais gerados pela pipeline Reversa de forma estritamente somente-leitura. Os arquivos lidos são:

- **`.reversa/state.json`**: Usado para extrair metadados sobre o progresso e checkpoints da engenharia reversa.
- **`_reversa_sdd/domain.md`**: Usado para extrair e renderizar a lista de Regras de Negócio e conceitos vigentes.
- **`_reversa_sdd/architecture.md`**: Usado para extrair detalhes de componentes do sistema legado.
- **`_reversa_sdd/adrs/` ou `claude-config/decisoes/`**: Usado para listar o histórico e o status de vigência das microdecisões de design arquitetural.

## 3. Estrutura do Arquivo de Saída (`harness-docs.html`)

O arquivo gerado é gravado na raiz do projeto (`harness-docs.html`) e conterá os blocos abaixo de forma embutida e autossuficiente:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Documentação do Harness CLI</title>
  <style>
    /* CSS Embutido Premium (Dark Theme, Grid Layout, Responsividade) */
  </style>
</head>
<body>
  <!-- Estrutura de Layout:
       - Header (Título e Busca)
       - Sidebar (Menu de seções e barra de progresso Reversa)
       - Content Area (Abas dinâmicas)
  -->
  <script>
    /* JS Embutido (Abas de navegação, busca/filtro cliente-side) */
  </script>
</body>
</html>
```
