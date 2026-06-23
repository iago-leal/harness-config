# Investigation: Documentação de Uso Autogerada em HTML

> Identificador: `002-documentacao-uso-html`
> Data: `2026-06-23`
> Roadmap: `_reversa_forward/002-documentacao-uso-html/roadmap.md`

## 1. Introspecção do `argparse` em Python

Para evitar duplicação manual de dados dos comandos e parâmetros, a melhor abordagem em Python é obter os metadados do parser `ArgumentParser` programaticamente.

No arquivo `harness-core/src/main.py`, a função de entrada instancia o `argparse.ArgumentParser`. Ao invés de executar a CLI, podemos expor o parser por meio de uma função auxiliar exportável (ex: `create_parser()`) que retorna a instância configurada do parser de CLI.
Dessa forma, o `DocumentationService` pode importar o parser do `main` e navegar recursivamente pela árvore de subparsers e ações:

```python
def extract_commands(parser):
    commands = []
    # Localiza o action correspondente a subparsers
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for choice, subparser in action.choices.items():
                cmd_info = {
                    "name": choice,
                    "help": subparser.description or subparser.help,
                    "arguments": []
                }
                for subaction in subparser._actions:
                    if subaction.dest == "help":
                        continue
                    cmd_info["arguments"].append({
                        "flags": subaction.option_strings,
                        "help": subaction.help,
                        "required": subaction.required,
                        "default": subaction.default
                    })
                commands.append(cmd_info)
    return commands
```

## 2. Servidor HTTP Embutido em Python

Para servir o HTML de maneira limpa localmente, a biblioteca padrão do Python possui o módulo `http.server`, que atende perfeitamente ao requisito de não ter dependências extras.

Implementação do `doc-serve`:
```python
import http.server
import socketserver

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

class SafeHandler(Handler):
    # Sobrescreve para responder apenas a requisição do arquivo específico 
    # harness-docs.html caso seja acessado via raiz
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.path = "/harness-docs.html"
        return super().do_GET()

def start_server():
    try:
        with socketserver.TCPServer(("", PORT), SafeHandler) as httpd:
            print(f"Servidor iniciado em http://localhost:{PORT}")
            print("Pressione Ctrl+C para encerrar.")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor finalizado pelo usuário.")
```

## 3. Design visual do HTML Standalone (Premium)

O design visual será embutido inteiramente em uma tag `<style>` no cabeçalho do HTML, eliminando chamadas a servidores remotos para manter a funcionalidade offline estável.

Diretrizes estéticas aplicadas:
- **Tema:** Dark mode elegante por padrão, com tons escuros (fundo `#121214`), cinza premium e detalhes de destaque em verde esmeralda (`#04d361`) ou azul clássico (`#495057`).
- **Layout:** Barra lateral de navegação fixa à esquerda (ou retraível) e área de conteúdo principal à direita com rolagem independente.
- **Interatividade:**
  - Campo de busca global com JavaScript Vanilla filtrando comandos e regras em tempo de execução ao digitar (`input` listener manipulando classes CSS `.hidden`).
  - Navegação por Abas: CLI Comandos, Regras de Negócio Legadas, Microdecisões de Design (ADRs) e Checkpoints da Reversa.
- **Dashboard de Progresso:** Um gráfico visual em SVG (como barra de progresso aninhada ou anel de porcentagem interativo) com os checkpoints do Reversa (concluídos vs pendentes) extraídos do `state.json`.
