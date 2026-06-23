# MD-0008 — Geração de Documentação Standalone por Introspecção de CLI

> Data: 2026-06-23
> Estado: **aceito**

## D: Decisão
Implementar um gerador de documentação centralizado (`DocumentationService`) no `harness-core` capaz de construir um arquivo único HTML autossuficiente (`harness-docs.html` na raiz do projeto) utilizando introspecção recursiva do `argparse.ArgumentParser` e parsing de regras de domínio no legado. O visual utiliza CSS dark mode moderno integrado de forma interna e Vanilla JS para busca instantânea cliente-side, e o comando `./harness doc-serve` expõe a documentação através de um servidor local HTTP nativo em Python (`http.server`).

## PORQUÊ: Justificativa
* **Introspecção de CLI:** Extrair dinamicamente a ajuda e os comandos configurados diretamente a partir do parser `ArgumentParser` no `main.py` elimina a necessidade de duplicar explicações de CLI no código e no HTML, garantindo documentação livre de discrepâncias.
* **Autossuficiência (Standalone):** Compilar estilos, interatividade e dados estruturados em um único arquivo HTML standalone garante portabilidade absoluta, permitindo que desenvolvedores e novos agentes leiam e consultem o manual de uso offline e em ambientes locais isolados de rede.
* **Aderência Offline e Sem Dependências:** O servidor de documentação integrado utiliza o módulo padrão do Python `http.server` de modo a não exigir bibliotecas externas adicionais no `requirements.txt` (como Flask ou FastAPI), mantendo a execução leve.

## DESCARTADO: Alternativas consideradas
* **Dependência de CDNs Web (Tailwind/Fontes):** Utilizar Tailwind CSS via CDN online para o layout do HTML. Descartado para prevenir quebras visuais e de legibilidade caso o desenvolvedor utilize a documentação em voos, sem conexão à internet ou sob firewalls restritos.
* **Ferramenta de Documentação Externa (ex: Sphinx ou MkDocs):** Descartada para evitar dependências volumosas no setup de ambiente do interpretador virtual.
