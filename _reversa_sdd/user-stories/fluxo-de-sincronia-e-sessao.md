# User Stories — harness-config

> Gerado pelo Redator em 2026-06-23
> Nível de Documentação: **Completo**

Este documento detalha as histórias de usuário (User Stories) e jornadas de interação típicas que descrevem como o desenvolvedor humano e os agentes de IA interagem com o ecossistema `harness-config`.

---

##  J-01: Inicialização Segura e Alerta de Sincronia (SessionStart)

```
Como desenvolvedor (humano ou IA)
Ao iniciar uma nova sessão de trabalho no repositório ativo
Quero que o sistema valide silenciosamente a sincronia local e remota do Git
Para que eu seja notificado de pendências de pull ou push sem que isso atrase o boot da CLI.
```

### Cenário 1: Repositório Atrasado (Remote à frente)
* **Dado** que a ramificação local possui commits em falta em relação ao remote origin.
* **E** que a janela de TTL do cache expirou ou o cache está vazio.
* **Quando** a CLI do Claude Code for aberta (disparando o evento `SessionStart`).
* **Então** o `sync-check.sh` deve rodar o `git ls-remote` e injetar um alerta no contexto adicional recomendando a execução imediata de `git pull --ff-only`.

### Cenário 2: Uso do Cache TTL (Evitar lentidão de boot)
* **Dado** que o hook rodou há 2 horas (TTL de 24h ativo).
* **Quando** uma nova sessão for aberta no editor.
* **Então** o script deve bypassar a chamada de rede e validar a consistência instantaneamente utilizando o hash armazenado no cache em disco.

---

## J-02: Formatação Automática no Pós-Edição (PostToolUse)

```
Como engenheiro de software
Ao realizar alterações e salvar código na IDE por meio de ganchos do agente
Quero que os arquivos de código sejam formatados imediatamente de forma silenciosa
Para que o repositório permaneça padronizado sem exigir execuções manuais de formatadores.
```

### Cenário 1: Edição de Código de Software
* **Dado** que o agente gravou uma modificação num arquivo de lógica funcional (ex: `main.py`).
* **Quando** o hook `PostToolUse` for disparado.
* **Então** o `format-on-edit.sh` deve detectar a raiz do projeto por meio do manifesto `pyproject.toml`, executar `ruff format` no arquivo e emitir o JSON `systemMessage` de conformidade.

---

## J-03: Encerramento de Sessão e Consolidação de Estado

```
Como desenvolvedor
Ao encerrar minhas atividades de desenvolvimento do dia
Quero que o ambiente compile o índice de microdecisões, ancore o commit HEAD e limpe hooks
Para que a sessão seja fechada de forma íntegra e esteja pronta para retomada segura em qualquer máquina.
```

### Cenário 1: Execução do Fechamento
* **Dado** que o desenvolvedor executou o comando `/encerrar-sessao`.
* **Quando** o fluxo for processado.
* **Então** o sistema deve commitar arquivos pendentes, escrever o hash Git HEAD âncora no arquivo `ESTADO-DA-SESSAO.md`, recalcular o grafo de backlinks de decisões em `microdecisoes.md` e sugerir a execução de `git push`.
