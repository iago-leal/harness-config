# Máquinas de Estado (State Machines) — harness-core

> Gerado pelo Detective em 2026-06-23
> Nível de Documentação: **Completo**

Este documento detalha o ciclo de vida e as transições de estado das entidades centrais do `harness-core` que possuem status explícitos: a **Sessão do Agente** e as **Microdecisões**.

---

## 🤝 1. Máquina de Estados: Sessão do Agente (`SessionState`)

O estado da sessão do agente local é persistido em `ESTADO-DA-SESSAO.md` e gerencia as transições de boot e encerramento.

```mermaid
stateDiagram-v2
    [*] --> INACTIVE : Arquivo ausente ou status=inactive
    
    INACTIVE --> ACTIVE : Comando: ./harness cmd resume\n(Gatilha SessionStart no agente)
    
    ACTIVE --> INACTIVE : Comando: ./harness cmd encerrar-sessao\n(Grava commit âncora)
    
    ACTIVE --> ACTIVE : Alterações de arquivos (PostToolUse)\nou novos commits Git
```

### ⚡ Transições e Condições (Sessão do Agente)

| Origem | Destino | Gatilho / Condição | Confiança |
| :--- | :--- | :--- | :--- |
| `INACTIVE` | `ACTIVE` | Execução de `cmd resume`. Se a hash do HEAD atual divergir da âncora anterior, emite alerta, mas avança. | 🟢 CONFIRMADO |
| `ACTIVE` | `INACTIVE` | Execução de `cmd encerrar-sessao`. Valida se o diretório do repositório está limpo e grava a hash do commit âncora no arquivo de estado. | 🟢 CONFIRMADO |

---

## 📄 2. Máquina de Estados: Microdecisão (`Decision`)

O status de vigência das decisões arquiteturais tomadas no projeto.

```mermaid
stateDiagram-v2
    [*] --> EM_REVISAO : Criação da proposta (Front-matter: estado=em-revisao)
    [*] --> ATIVO : Decisão trivial aceita (Front-matter: estado=ativo)
    
    EM_REVISAO --> ATIVO : Homologada e aprovada pelo Humano
    EM_REVISAO --> REJEITADO : Descartada ou inviabilizada
    
    ATIVO --> REJEITADO : Substituída por nova decisão (YAML: relacao "substitui MD-XXXX")
    ATIVO --> EM_REVISAO : Reaberta para alteração ou refinamento técnico
```

### ⚡ Transições e Condições (Microdecisão)

| Origem | Destino | Gatilho / Condição | Confiança |
| :--- | :--- | :--- | :--- |
| `EM_REVISAO` | `ATIVO` | Alteração manual do campo `estado` no front-matter do markdown correspondente. | 🟢 CONFIRMADO |
| `ATIVO` | `REJEITADO` | Criação de uma microdecisão que possui a relação `substitui MD-XXXX`. O indexador recompila o backlinks e atualiza o grafo. | 🟢 CONFIRMADO |
