# Onboarding: Reprodutibilidade e Configuração Viva de Formatação

> Identificador: `008-reprodutibilidade-e-config`
> Data: `2026-06-24`

Este guia instrui como validar localmente as melhorias de reprodutibilidade e a ativação dinâmica de configurações de formatação introduzidas por esta feature.

---

## 1. Validando a Reprodutibilidade com `uv`

1. Certifique-se de que o `uv` está instalado no sistema local:
   ```bash
   uv --version
   ```
2. Delete o diretório `.venv` existente dentro do `harness-core` para simular uma nova instalação limpa:
   ```bash
   rm -rf harness-core/.venv
   ```
3. Crie e sincronize o ambiente virtual usando o `uv` com base no arquivo de dependências travadas:
   ```bash
   cd harness-core
   uv venv
   uv pip sync requirements.txt
   ```
4. Execute os testes locais para confirmar o setup bem-sucedido:
   ```bash
   PYTHONPATH=. .venv/bin/pytest
   ```

---

## 2. Validando a Configuração Viva do Formatador

### Caso A: Opt-out customizado
1. No seu arquivo `harness-core/harness.toml`, edite ou adicione a configuração do opt-out com um nome diferente do padrão:
   ```toml
   [formatting]
   opt_out_file = ".ignorar-autoformatacao"
   ```
2. Crie um arquivo com esse nome em um diretório de testes:
   ```bash
   touch harness-core/tests/.ignorar-autoformatacao
   ```
3. Crie um arquivo Python mal formatado no mesmo diretório:
   ```bash
   echo "x   =    1" > harness-core/tests/arquivo_teste.py
   ```
4. Execute o formatador via CLI:
   ```bash
   ./harness format harness-core/tests/arquivo_teste.py
   ```
5. Verifique que o arquivo **não** foi formatado (a formatação foi cancelada por causa do opt-out configurado dinamicamente).
6. Remova os arquivos temporários após o teste:
   ```bash
   rm harness-core/tests/.ignorar-autoformatacao harness-core/tests/arquivo_teste.py
   ```

### Caso B: Exclusão por caminhos de diretório e glob patterns
1. Edite `harness-core/harness.toml` para incluir padrões de exclusão:
   ```toml
   [formatting]
   exclude_paths = ["tests/excluidos/*", "**/*.excluida.py"]
   ```
2. Crie a pasta `tests/excluidos` se não existir, e adicione um arquivo Python nela:
   ```bash
   mkdir -p harness-core/tests/excluidos
   echo "y   =    2" > harness-core/tests/excluidos/teste.py
   ```
3. Crie outro arquivo fora da pasta mas casando com o padrão de extensão:
   ```bash
   echo "z   =    3" > harness-core/tests/qualquer.excluida.py
   ```
4. Execute a formatação de ambos os arquivos:
   ```bash
   ./harness format harness-core/tests/excluidos/teste.py
   ./harness format harness-core/tests/qualquer.excluida.py
   ```
5. Confirme que ambos os arquivos continuam sem formatação.
6. Limpe o diretório de testes:
   ```bash
   rm -rf harness-core/tests/excluidos harness-core/tests/qualquer.excluida.py
   ```
