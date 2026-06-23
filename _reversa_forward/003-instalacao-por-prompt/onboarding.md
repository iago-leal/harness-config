# Onboarding: Instalação do Harness por Prompt Estruturado

> Identificador: `003-instalacao-por-prompt`
> Data: `2026-06-23`

Guia executável para validar a feature pela primeira vez, após a implementação (`/reversa-coding`).

---

## 1. Pré-requisitos

O ambiente virtual do `harness-core` precisa existir (ele será também o que o próprio prompt instala):

```bash
cd harness-core
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

---

## 2. Gerar o prompt de instalação

```bash
# Imprime o prompt completo, parametrizado pelo active_harness do harness.toml
./harness install-prompt
```

Resultado esperado: um texto ordenado e copiável, contendo as etapas de venv/dependências, wrapper, aplicação dos ganchos de ciclo de vida do harness ativo e uma seção final de verificação de saúde. O texto deve mencionar explicitamente o `.claude/settings.json` do **projeto** (nunca `~/.claude`) e sinalizar a lacuna conhecida do `SessionStart` (regressão de MD-0001).

---

## 3. Validar a parametrização por harness

```bash
# Trocar temporariamente o harness ativo e conferir que o bloco de ganchos muda
# (editar harness.toml: [harness] active_harness = "gemini")
./harness install-prompt | grep -i gemini
# Reverter para "claude" ao final
```

Resultado esperado: o bloco de ganchos reflete o mecanismo do harness selecionado (Claude via `settings.json` `hooks`; Gemini via ponte `context.*`). O perfil de `antigravity` deve avisar que o mecanismo ainda não está confirmado.

---

## 4. Rodar os testes da feature

```bash
cd harness-core
.venv/bin/python3 -m pytest tests/test_install.py -q
cd ..
```

Resultado esperado: verde. Os testes asseguram que o prompt contém cada etapa obrigatória, a seção de health-check e o conteúdo correto por harness.

---

## 5. Ensaiar a instalação a partir do prompt (opcional)

Num diretório de rascunho com uma cópia do `harness-core`, siga manualmente os passos que o prompt descreve e confirme que, ao final, `./harness decisions` retorna verde e os ganchos do projeto apontam para a CLI. Rode o prompt duas vezes e confirme que a segunda execução não corrompe nada (idempotência, RN-02).

---

## 6. Verificação de saúde manual

Após seguir o prompt, o health-check deve reportar, item a item: venv presente, wrapper executável, ganchos aplicados, `decisions` verde — e a lacuna do `SessionStart` marcada como **pendente conhecida** (não como falha de instalação).
