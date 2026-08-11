# Contrato: trecho de guidance gravado pelo `init` no CLAUDE.md / AGENTS.md

> Identificador: `028-indice-decisoes-sob-demanda`
> Tipo: arquivo de guidance do projeto-alvo, escrita única na instalação (decisão D3 do clarify, à maneira do Reversa).

## 1. Alvo

| `active_harness` | Arquivo | Confidência |
|------------------|---------|-------------|
| `claude` | `CLAUDE.md` na raiz do projeto | 🟢 |
| `antigravity` | `AGENTS.md` na raiz do projeto | 🟡 (confirmar no coding o arquivo de guidance efetivo da engine) |

## 2. Comportamento do `init`

1. Se o arquivo-alvo NÃO existe: cria com o trecho como conteúdo inicial.
2. Se existe e NÃO contém o marcador: anexa o trecho ao final, precedido de linha em branco.
3. Se existe e JÁ contém o marcador: não escreve nada (idempotência por detecção de substring do marcador, não do conteúdo).
4. O `upgrade` NUNCA toca o trecho; edições manuais do usuário dentro da seção são preservadas para sempre.

## 3. Marcador e conteúdo

Marcador estável (abre a seção; a detecção usa só esta linha):

```markdown
<!-- harness:decisoes -->
```

Trecho gravado (texto de referência; ajustes de redação no coding são livres, o marcador não):

```markdown
<!-- harness:decisoes -->
## Microdecisões do projeto

Este projeto registra decisões técnicas em fichas `.harness/decisoes/MD-NNNN.md`.
No início da sessão é injetada uma visão compacta (as mais recentes). Antes de
buscas amplas ou de decidir algo já decidido, consulte o índice completo em
`.harness/microdecisoes.md` e abra a ficha específica quando precisar do contexto.
Registre decisões novas com uma ficha; o índice e a visão compacta são derivados
automaticamente (`./harness decisions`). Não os edite à mão.
```

- Paths no trecho refletem a config real do projeto no momento do init (`decisions.dir`, `decisions.index_file`).
- Sem timestamp, sem versão do core, sem nada volátil: o trecho precisa envelhecer bem, pois nunca será reescrito.

## 4. Riscos cobertos

- Usuário remove o marcador mas mantém o texto: um re-init duplica o conteúdo. Aceito e documentado (marcador é o contrato de idempotência); severidade baixa, correção manual trivial.
- Projeto sem raiz git: o `init` já se recusa antes (MD-0007); este contrato herda o comportamento.
