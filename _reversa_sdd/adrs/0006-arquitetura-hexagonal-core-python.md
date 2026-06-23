# MD-0006 — Arquitetura Hexagonal no Core Python

> Data: 2026-06-23
> Estado: **aceito**

## D: Decisão
Organizar o código do núcleo Python (`harness-core`) seguindo o padrão de Arquitetura Hexagonal (Portas e Adaptadores). A lógica de negócio reside pura sob `src/core/` (como serviços e domínios) e interage com o sistema de arquivos, subprocessos locais do host e Git exclusivamente por meio de interfaces (Portas) implementadas fisicamente por adaptadores em `src/adapters/`.

## PORQUÊ: Justificativa
* **Testabilidade Isolada:** O pytest pode simular operações de arquivos e comandos Git injetando stubs e mocks (como `StubFileSystemAdapter`) de forma simples, sem necessidade de tocar no disco real ou repositório Git físico nas asserções de teste.
* **Desacoplamento de Infraestrutura:** Mudanças de interpretador, dependência de biblioteca de terceiros (ex: usar outra biblioteca de Git) ou sistema operacional não vazam para a lógica do ciclo de vida das sessões.
* **Portabilidade:** Facilita portar o Harness para ser executado no navegador, cloud ou outros hosts de automação.

## DESCARTADO: Alternativas consideradas
* **Scripts Acoplados Simples:** Código procedural Python chamando diretamente `os.path` e `subprocess.run` nas funções principais. Descartado porque impede testes unitários determinísticos rápidos (pytest exigiria fixtures pesadas de criação de pastas temporárias reais a cada execução).
